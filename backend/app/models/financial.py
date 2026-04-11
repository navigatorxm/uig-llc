"""Financial models — wallet, transactions, and cost tracking."""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text
from app.database import Base


class TransactionType(str, enum.Enum):
    credit = "credit"
    debit = "debit"


class TransactionCategory(str, enum.Enum):
    ai_usage = "ai_usage"           # Claude, GPT, etc.
    scraping = "scraping"           # Apify, Playwright
    outreach_sms = "outreach_sms"   # Twilio
    outreach_email = "outreach_email"  # SendGrid
    crm = "crm"                     # HubSpot
    storage = "storage"             # Google Drive
    subscription = "subscription"
    manual_topup = "manual_topup"
    refund = "refund"
    other = "other"


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    category = Column(Enum(TransactionCategory), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=True)  # external ref (Stripe, etc.)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), nullable=False)  # "claude-3-sonnet", "gpt-4o", etc.
    endpoint = Column(String(255), nullable=True)  # which feature used it
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
