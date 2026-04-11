"""Admin costs & AI usage router — monitor spending across all services."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.financial import WalletTransaction, AIUsageLog, TransactionType, TransactionCategory
from app.models.admin_user import AdminUser
from app.routers.admin_auth import get_admin_user, require_admin

router = APIRouter(
    prefix="/api/admin/costs",
    tags=["Admin Costs & Credits"],
    dependencies=[Depends(get_admin_user)],
)


# --- Schemas ---

class WalletTopupRequest(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    reference_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    transaction_type: TransactionType
    amount: float
    currency: str
    category: TransactionCategory
    description: Optional[str]
    reference_id: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class AILogResponse(BaseModel):
    id: int
    model: str
    endpoint: Optional[str]
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}

class RecordUsageRequest(BaseModel):
    model: str
    endpoint: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: Optional[int] = None


# --- Endpoints ---

@router.get("/overview")
def cost_overview(days: int = 30, db: Session = Depends(get_db)):
    """Get spending overview across all categories."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Wallet balance
    total_credits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.credit
    ).scalar()
    total_debits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.debit
    ).scalar()
    balance = total_credits - total_debits

    # Spending by category (last N days)
    by_category = db.query(
        WalletTransaction.category,
        func.sum(WalletTransaction.amount),
    ).filter(
        WalletTransaction.transaction_type == TransactionType.debit,
        WalletTransaction.created_at >= cutoff,
    ).group_by(WalletTransaction.category).all()

    # AI usage totals
    ai_total_cost = db.query(func.coalesce(func.sum(AIUsageLog.cost_usd), 0)).filter(
        AIUsageLog.created_at >= cutoff,
    ).scalar()
    ai_total_tokens = db.query(
        func.coalesce(func.sum(AIUsageLog.tokens_in), 0),
        func.coalesce(func.sum(AIUsageLog.tokens_out), 0),
    ).filter(AIUsageLog.created_at >= cutoff).first()

    # AI usage by model
    by_model = db.query(
        AIUsageLog.model,
        func.count(AIUsageLog.id),
        func.sum(AIUsageLog.tokens_in),
        func.sum(AIUsageLog.tokens_out),
        func.sum(AIUsageLog.cost_usd),
    ).filter(
        AIUsageLog.created_at >= cutoff,
    ).group_by(AIUsageLog.model).all()

    return {
        "wallet": {
            "balance_usd": round(balance, 2),
            "total_credits": round(total_credits, 2),
            "total_debits": round(total_debits, 2),
        },
        "spending_by_category": {
            cat.value: round(amount, 2) for cat, amount in by_category
        },
        "ai_usage": {
            "total_cost_usd": round(ai_total_cost, 4),
            "total_tokens_in": ai_total_tokens[0] if ai_total_tokens else 0,
            "total_tokens_out": ai_total_tokens[1] if ai_total_tokens else 0,
            "by_model": [
                {
                    "model": model,
                    "requests": count,
                    "tokens_in": t_in,
                    "tokens_out": t_out,
                    "cost_usd": round(cost, 4),
                }
                for model, count, t_in, t_out, cost in by_model
            ],
        },
        "period_days": days,
    }


@router.post("/wallet/topup", response_model=TransactionResponse, status_code=201)
def wallet_topup(
    req: WalletTopupRequest,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Add credits to the wallet."""
    tx = WalletTransaction(
        transaction_type=TransactionType.credit,
        amount=req.amount,
        currency=req.currency,
        category=TransactionCategory.manual_topup,
        description=req.description or f"Manual top-up by {admin.full_name}",
        reference_id=req.reference_id,
        created_by=admin.email,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    category: Optional[TransactionCategory] = None,
    tx_type: Optional[TransactionType] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    """List wallet transactions."""
    query = db.query(WalletTransaction)
    if category:
        query = query.filter(WalletTransaction.category == category)
    if tx_type:
        query = query.filter(WalletTransaction.transaction_type == tx_type)
    return query.order_by(WalletTransaction.created_at.desc()).limit(limit).all()


@router.post("/ai-usage", response_model=AILogResponse, status_code=201)
def record_ai_usage(req: RecordUsageRequest, db: Session = Depends(get_db)):
    """Record an AI API usage event (called internally by services)."""
    log = AIUsageLog(
        model=req.model,
        endpoint=req.endpoint,
        tokens_in=req.tokens_in,
        tokens_out=req.tokens_out,
        cost_usd=req.cost_usd,
        latency_ms=req.latency_ms,
    )
    db.add(log)

    # Auto-create debit transaction
    if req.cost_usd > 0:
        tx = WalletTransaction(
            transaction_type=TransactionType.debit,
            amount=req.cost_usd,
            currency="USD",
            category=TransactionCategory.ai_usage,
            description=f"{req.model} — {req.tokens_in + req.tokens_out} tokens",
        )
        db.add(tx)

    db.commit()
    db.refresh(log)
    return log


@router.get("/ai-usage", response_model=List[AILogResponse])
def list_ai_usage(
    model: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    """List AI usage logs."""
    query = db.query(AIUsageLog)
    if model:
        query = query.filter(AIUsageLog.model == model)
    return query.order_by(AIUsageLog.created_at.desc()).limit(limit).all()


@router.get("/daily-breakdown")
def daily_breakdown(days: int = 7, db: Session = Depends(get_db)):
    """Day-by-day spending breakdown for charts."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    daily = db.query(
        func.date(WalletTransaction.created_at).label("day"),
        func.sum(WalletTransaction.amount),
    ).filter(
        WalletTransaction.transaction_type == TransactionType.debit,
        WalletTransaction.created_at >= cutoff,
    ).group_by(func.date(WalletTransaction.created_at)).all()

    return {
        "daily_spending": [
            {"date": str(day), "amount_usd": round(amount, 2)}
            for day, amount in daily
        ]
    }
