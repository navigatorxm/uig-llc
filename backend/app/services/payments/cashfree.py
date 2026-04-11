"""CashFree Payment Gateway service — for LPI certificate fee collection (INR)."""
import hmac
import hashlib
import logging
import httpx
from datetime import datetime, timezone
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

CASHFREE_BASE_URL = {
    "production": "https://api.cashfree.com/pg",
    "sandbox": "https://sandbox.cashfree.com/pg",
}


class CashFreeService:
    """Handles payment order creation, verification, and refunds via CashFree PG."""

    def __init__(self):
        self.app_id = settings.cashfree_app_id
        self.secret_key = settings.cashfree_secret_key
        self.env = settings.cashfree_environment  # "production" or "sandbox"
        self.base_url = CASHFREE_BASE_URL[self.env]
        self.api_version = "2023-08-01"

    # ------------------------------------------------------------------ #
    #  Headers
    # ------------------------------------------------------------------ #
    def _headers(self) -> dict:
        return {
            "x-client-id": self.app_id,
            "x-client-secret": self.secret_key,
            "x-api-version": self.api_version,
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    #  Create Order
    # ------------------------------------------------------------------ #
    def create_order(
        self,
        order_id: str,
        amount_inr: float,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        return_url: str,
        meta: Optional[dict] = None,
    ) -> dict:
        """
        Create a CashFree payment order.
        Returns the payment_session_id needed by the JS SDK to open checkout.
        """
        payload = {
            "order_id": order_id,
            "order_amount": round(amount_inr, 2),
            "order_currency": "INR",
            "customer_details": {
                "customer_id": f"cust_{customer_phone.replace('+', '').replace(' ', '')}",
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
            },
            "order_meta": {
                "return_url": f"{return_url}?order_id={{order_id}}&order_token={{order_token}}",
                "notify_url": f"{settings.cashfree_webhook_url}",
            },
            "order_tags": meta or {},
        }

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base_url}/orders",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"CashFree order created: {order_id} — ₹{amount_inr}")
                return {
                    "order_id": data["order_id"],
                    "payment_session_id": data["payment_session_id"],
                    "order_status": data["order_status"],
                    "order_token": data.get("order_token", ""),
                }
        except httpx.HTTPStatusError as exc:
            logger.error(f"CashFree create_order error: {exc.response.text}")
            raise

    # ------------------------------------------------------------------ #
    #  Verify Order Status
    # ------------------------------------------------------------------ #
    def get_order_status(self, order_id: str) -> dict:
        """Fetch current status of a payment order."""
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    f"{self.base_url}/orders/{order_id}",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "order_id": data["order_id"],
                    "order_status": data["order_status"],  # PAID | ACTIVE | EXPIRED | ...
                    "order_amount": data["order_amount"],
                    "cf_order_id": data.get("cf_order_id"),
                }
        except httpx.HTTPStatusError as exc:
            logger.error(f"CashFree get_order_status error: {exc.response.text}")
            raise

    # ------------------------------------------------------------------ #
    #  Webhook Signature Verification
    # ------------------------------------------------------------------ #
    def verify_webhook_signature(self, raw_body: bytes, timestamp: str, signature: str) -> bool:
        """
        Verify incoming CashFree webhook.
        CashFree signs with: HMAC-SHA256(timestamp + raw_body, secret_key)
        """
        message = timestamp.encode() + raw_body
        expected = hmac.new(
            self.secret_key.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    # ------------------------------------------------------------------ #
    #  Refund
    # ------------------------------------------------------------------ #
    def initiate_refund(self, order_id: str, refund_id: str, amount_inr: float, reason: str = "Customer request") -> dict:
        """Initiate a partial/full refund for a paid order."""
        payload = {
            "refund_amount": round(amount_inr, 2),
            "refund_id": refund_id,
            "refund_note": reason,
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base_url}/orders/{order_id}/refunds",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"CashFree refund initiated: {refund_id} for order {order_id} — ₹{amount_inr}")
                return data
        except httpx.HTTPStatusError as exc:
            logger.error(f"CashFree refund error: {exc.response.text}")
            raise
