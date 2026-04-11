import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class PipelineStage(str, enum.Enum):
    # Active outreach stages
    new_lead = "new_lead"
    contact_initiated = "contact_initiated"
    response_received = "response_received"
    qualified = "qualified"
    docs_requested = "docs_requested"
    docs_received = "docs_received"
    under_verification = "under_verification"
    approved = "approved"
    visit_scheduled = "visit_scheduled"
    closed_won = "closed_won"
    closed_lost = "closed_lost"
    # Holding stages — for re-engagement campaigns
    cold_lead = "cold_lead"          # No response after 48h (5 follow-ups exhausted)
    pending_docs = "pending_docs"    # Responded but docs incomplete after 14 days


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String(255), nullable=False)
    phone = Column(String(20), index=True)
    email = Column(String(255), index=True)
    whatsapp = Column(String(20))

    pipeline_stage = Column(Enum(PipelineStage), default=PipelineStage.new_lead, nullable=False, index=True)
    lead_score = Column(Float, default=0.0)
    lead_score_breakdown = Column(Text)  # JSON string

    hubspot_contact_id = Column(String(100), unique=True, nullable=True)

    first_contact_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    contact_attempt_count = Column(Integer, default=0)
    response_received = Column(Boolean, default=False)
    interested = Column(Boolean, nullable=True)

    notes = Column(Text)
    assigned_to = Column(String(255))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    properties = relationship("Property", back_populates="lead")
    documents = relationship("Document", back_populates="lead")
    deals = relationship("Deal", back_populates="lead")
    outreach_logs = relationship("OutreachLog", back_populates="lead")
