import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DealType(str, enum.Enum):
    buy = "buy"
    rent = "rent"


class DealStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)

    deal_type = Column(Enum(DealType), nullable=False)
    status = Column(Enum(DealStatus), default=DealStatus.pending, nullable=False, index=True)

    agreed_price = Column(Float, nullable=True)
    price_currency = Column(String(10), default="INR")

    hubspot_deal_id = Column(String(100), unique=True, nullable=True)

    site_visit_scheduled_at = Column(DateTime, nullable=True)
    agreement_signed_at = Column(DateTime, nullable=True)
    payment_completed_at = Column(DateTime, nullable=True)

    notes = Column(Text)

    lead = relationship("Lead", back_populates="deals")
    property = relationship("Property")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
