import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class OutreachChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"


class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    channel = Column(Enum(OutreachChannel), nullable=False)
    message_template = Column(String(100))
    message_body = Column(Text)

    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered = Column(Boolean, nullable=True)
    delivery_sid = Column(String(255))  # Twilio SID or SendGrid message id

    response_text = Column(Text, nullable=True)
    response_at = Column(DateTime, nullable=True)

    lead = relationship("Lead", back_populates="outreach_logs")
