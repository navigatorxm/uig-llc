"""Admin accounts & wallet router — financial management dashboard."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.financial import WalletTransaction, TransactionType, TransactionCategory
from app.models.admin_user import AdminUser
from app.routers.admin_auth import get_admin_user, require_admin

router = APIRouter(
    prefix="/api/admin/accounts",
    tags=["Admin Accounts"],
    dependencies=[Depends(get_admin_user)],
)


class ManualTransactionRequest(BaseModel):
    transaction_type: TransactionType
    amount: float
    currency: str = "INR"
    category: TransactionCategory
    description: str
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


@router.get("/summary")
def accounts_summary(db: Session = Depends(get_db)):
    """Financial summary — balance, income, expenses, by category."""
    total_credits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.credit
    ).scalar()
    total_debits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.debit
    ).scalar()

    # Monthly
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0)
    month_credits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.credit,
        WalletTransaction.created_at >= month_start,
    ).scalar()
    month_debits = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.transaction_type == TransactionType.debit,
        WalletTransaction.created_at >= month_start,
    ).scalar()

    # By category
    by_category = db.query(
        WalletTransaction.category,
        WalletTransaction.transaction_type,
        func.sum(WalletTransaction.amount),
        func.count(WalletTransaction.id),
    ).group_by(WalletTransaction.category, WalletTransaction.transaction_type).all()

    breakdown = {}
    for cat, tx_type, amount, count in by_category:
        key = cat.value
        if key not in breakdown:
            breakdown[key] = {"credits": 0, "debits": 0, "transactions": 0}
        if tx_type == TransactionType.credit:
            breakdown[key]["credits"] = round(amount, 2)
        else:
            breakdown[key]["debits"] = round(amount, 2)
        breakdown[key]["transactions"] += count

    return {
        "balance": round(total_credits - total_debits, 2),
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2),
        "this_month": {
            "credits": round(month_credits, 2),
            "debits": round(month_debits, 2),
            "net": round(month_credits - month_debits, 2),
        },
        "by_category": breakdown,
    }


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def record_transaction(
    req: ManualTransactionRequest,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Record a manual transaction (top-up, expense, refund, etc.)."""
    tx = WalletTransaction(
        transaction_type=req.transaction_type,
        amount=req.amount,
        currency=req.currency,
        category=req.category,
        description=req.description,
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
    days: int = Query(default=30, le=365),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    """List transactions with filters."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(WalletTransaction).filter(WalletTransaction.created_at >= cutoff)
    if category:
        query = query.filter(WalletTransaction.category == category)
    if tx_type:
        query = query.filter(WalletTransaction.transaction_type == tx_type)
    return query.order_by(WalletTransaction.created_at.desc()).limit(limit).all()


@router.get("/monthly-trend")
def monthly_trend(months: int = 6, db: Session = Depends(get_db)):
    """Monthly income vs expense trend for charts."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 31)
    monthly = db.query(
        func.date_trunc("month", WalletTransaction.created_at).label("month"),
        WalletTransaction.transaction_type,
        func.sum(WalletTransaction.amount),
    ).filter(
        WalletTransaction.created_at >= cutoff,
    ).group_by("month", WalletTransaction.transaction_type).all()

    data = {}
    for month, tx_type, amount in monthly:
        key = str(month)[:7]  # "2026-04"
        if key not in data:
            data[key] = {"credits": 0, "debits": 0}
        if tx_type == TransactionType.credit:
            data[key]["credits"] = round(amount, 2)
        else:
            data[key]["debits"] = round(amount, 2)

    return {
        "monthly": [
            {"month": k, "credits": v["credits"], "debits": v["debits"], "net": round(v["credits"] - v["debits"], 2)}
            for k, v in sorted(data.items())
        ]
    }
