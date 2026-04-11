"""SQLAlchemy model for issued LPI certificates."""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LPICertificateRecord(Base):
    """Database record for an issued LPI certificate."""
    __tablename__ = "lpi_certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(100), unique=True, nullable=False, index=True)
    lpi_codes = Column(JSON, nullable=False)          # List of LPI codes
    property_address = Column(Text, nullable=False)
    owner_name = Column(String(255))
    city = Column(String(100), index=True)
    state = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    total_area_sqm = Column(Float)

    # Zone data
    in_airport_zone = Column(Boolean, default=False, index=True)
    nearest_airport_iata = Column(String(10))
    airport_distance_km = Column(Float)
    zone_priority = Column(String(20))                # critical | high | elevated | standard

    # Certificate status
    status = Column(String(20), default="valid")      # valid | expired | suspended
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    valid_until = Column(DateTime)
    flags = Column(JSON, default=list)                 # ["AIRPORT_ZONE_PROPERTY", ...]

    # Scan details
    satellite_id = Column(String(50), default="UIG-SAT-3")
    scan_resolution_cm = Column(Float, default=10.0)
    lidar_scan_date = Column(DateTime)
    encroachment_detected = Column(Boolean, default=False)
    flood_risk_score = Column(Float, default=0.0)
    seismic_zone = Column(String(5))

    # Fee tracking
    issuance_fee_inr = Column(Float, default=15000.0)
    fee_paid = Column(Boolean, default=False)
    fee_paid_at = Column(DateTime, nullable=True)

    # Link to lead (if this cert was issued as part of acquisition process)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    issued_by_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)

    lead = relationship("Lead")
    issued_by_agent = relationship("Agent")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
