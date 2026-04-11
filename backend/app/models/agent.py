"""SQLAlchemy model for real estate agent partners."""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AgentTier(str, enum.Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class AgentStatus(str, enum.Enum):
    prospect = "prospect"
    pitched = "pitched"
    follow_up = "follow_up"
    onboarded = "onboarded"
    active = "active"
    inactive = "inactive"
    churned = "churned"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    agency_name = Column(String(255))
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100))
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    whatsapp = Column(String(20))
    rera_number = Column(String(50), unique=True, nullable=True)

    specialization = Column(String(50), default="mixed")
    tier = Column(Enum(AgentTier), default=AgentTier.bronze)
    status = Column(Enum(AgentStatus), default=AgentStatus.prospect, index=True)

    # LPI License
    lpi_license_active = Column(Boolean, default=False)
    lpi_license_issued_at = Column(DateTime, nullable=True)
    lpi_license_expiry = Column(DateTime, nullable=True)
    lpi_verifications_count = Column(Integer, default=0)

    # Performance
    total_referrals = Column(Integer, default=0)
    successful_conversions = Column(Integer, default=0)
    active_leads_count = Column(Integer, default=0)
    total_revenue_generated_inr = Column(Float, default=0.0)
    total_fees_paid_inr = Column(Float, default=0.0)

    # Zone Assignment
    assigned_airport_zones = Column(JSON, default=list)   # ["DEL", "BOM"]
    preferred_portals = Column(JSON, default=list)

    # Outreach tracking
    first_contact_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    contact_attempts = Column(Integer, default=0)
    responded = Column(Boolean, default=False)

    hubspot_contact_id = Column(String(100), nullable=True)
    notes = Column(Text)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
