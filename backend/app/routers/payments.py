"""Payments router — CashFree payment gateway for LPI certificate fee collection."""
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models.lpi_certificate import LPICertificateRecord
from app.models.financial import WalletTransaction, TransactionType, TransactionCategory
from app.services.payments.cashfree import CashFreeService
from app.auth.jwt import get_current_user
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

CASHFREE_LPI_FEE_INR = 15000.0  # Standard LPI certificate issuance fee


# ------------------------------------------------------------------ #
#  Schemas
# ------------------------------------------------------------------ #
class CreatePaymentOrderRequest(BaseModel):
    certificate_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    return_url: Optional[str] = f"https://lpi.directory/payment/success"


class PaymentOrderResponse(BaseModel):
    order_id: str
    payment_session_id: str
    amount_inr: float
    certificate_id: str


class PaymentStatusResponse(BaseModel):
    order_id: str
    certificate_id: str
    status: str  # PAID | ACTIVE | EXPIRED
    amount_inr: float


# ------------------------------------------------------------------ #
#  Create Payment Order
# ------------------------------------------------------------------ #
@router.post("/payments/lpi/create-order", response_model=PaymentOrderResponse)
def create_lpi_payment_order(
    req: CreatePaymentOrderRequest,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Create a CashFree payment order for an LPI certificate fee.
    Frontend should use the returned payment_session_id to open the CashFree JS checkout.
    """
    # Validate certificate exists
    cert = db.query(LPICertificateRecord).filter(
        LPICertificateRecord.certificate_id == req.certificate_id
    ).first()
    if not cert:
        raise HTTPException(status_code=404, detail="LPI certificate not found")

    if cert.fee_paid:
        raise HTTPException(status_code=400, detail="Fee for this certificate has already been paid")

    order_id = f"LPI-{req.certificate_id.replace('/', '-')}-{uuid.uuid4().hex[:8].upper()}"

    try:
        cf = CashFreeService()
        result = cf.create_order(
            order_id=order_id,
            amount_inr=CASHFREE_LPI_FEE_INR,
            customer_name=req.customer_name,
            customer_email=req.customer_email,
            customer_phone=req.customer_phone,
            return_url=req.return_url,
            meta={"certificate_id": req.certificate_id},
        )
    except Exception as exc:
        logger.error(f"CashFree order creation failed: {exc}")
        raise HTTPException(status_code=502, detail=f"Payment gateway error: {exc}")

    return PaymentOrderResponse(
        order_id=result["order_id"],
        payment_session_id=result["payment_session_id"],
        amount_inr=CASHFREE_LPI_FEE_INR,
        certificate_id=req.certificate_id,
    )


# ------------------------------------------------------------------ #
#  Check Payment Status
# ------------------------------------------------------------------ #
@router.get("/payments/lpi/status/{order_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    order_id: str,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Check payment status and auto-mark certificate as paid if PAID."""
    try:
        cf = CashFreeService()
        result = cf.get_order_status(order_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gateway error: {exc}")

    # Extract certificate_id from order_id pattern: LPI-<certid>-<uuid>
    parts = order_id.split("-")
    cert_id_parts = parts[1:-1] if len(parts) > 2 else []
    cert_id = "-".join(cert_id_parts) if cert_id_parts else ""

    # Auto-confirm if paid
    if result["order_status"] == "PAID" and cert_id:
        cert = db.query(LPICertificateRecord).filter(
            LPICertificateRecord.certificate_id == cert_id
        ).first()
        if cert and not cert.fee_paid:
            cert.fee_paid = True
            cert.fee_paid_at = datetime.now(timezone.utc)
            db.add(WalletTransaction(
                transaction_type=TransactionType.credit,
                amount=CASHFREE_LPI_FEE_INR,
                currency="INR",
                category=TransactionCategory.other,
                description=f"LPI certificate fee — {cert_id}",
                reference_id=order_id,
            ))
            db.commit()

    return PaymentStatusResponse(
        order_id=order_id,
        certificate_id=cert_id,
        status=result["order_status"],
        amount_inr=result["order_amount"],
    )


# ------------------------------------------------------------------ #
#  CashFree Webhook (no auth — signed by CashFree)
# ------------------------------------------------------------------ #
@router.post("/webhooks/cashfree")
async def cashfree_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_webhook_timestamp: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None),
):
    """
    Handle CashFree payment webhooks.
    CashFree sends PAYMENT_SUCCESS, PAYMENT_FAILED events here.
    """
    raw_body = await request.body()

    # Verify signature
    if x_webhook_timestamp and x_webhook_signature:
        try:
            cf = CashFreeService()
            if not cf.verify_webhook_signature(raw_body, x_webhook_timestamp, x_webhook_signature):
                logger.warning("CashFree webhook signature mismatch — rejected")
                raise HTTPException(status_code=403, detail="Invalid webhook signature")
        except Exception as exc:
            logger.error(f"Webhook verification error: {exc}")

    try:
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data", {})
        order = data.get("order", {})
        order_id = order.get("order_id", "")

        logger.info(f"CashFree webhook: {event_type} for order {order_id}")

        if event_type == "PAYMENT_SUCCESS":
            # Extract certificate_id from order tags or order_id
            order_tags = order.get("order_tags", {})
            cert_id = order_tags.get("certificate_id", "")

            if cert_id:
                cert = db.query(LPICertificateRecord).filter(
                    LPICertificateRecord.certificate_id == cert_id
                ).first()
                if cert and not cert.fee_paid:
                    cert.fee_paid = True
                    cert.fee_paid_at = datetime.now(timezone.utc)
                    amount = order.get("order_amount", CASHFREE_LPI_FEE_INR)
                    db.add(WalletTransaction(
                        transaction_type=TransactionType.credit,
                        amount=float(amount),
                        currency="INR",
                        category=TransactionCategory.other,
                        description=f"LPI certificate fee — {cert_id} [webhook]",
                        reference_id=order_id,
                    ))
                    db.commit()
                    logger.info(f"Certificate {cert_id} marked as paid via webhook")

        elif event_type == "PAYMENT_FAILED":
            logger.warning(f"Payment FAILED for order {order_id}")

    except Exception as exc:
        logger.error(f"CashFree webhook processing error: {exc}")

    return {"status": "ok"}
