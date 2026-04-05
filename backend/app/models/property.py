import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    plot = "plot"
    commercial = "commercial"
    office = "office"
    warehouse = "warehouse"
    farmhouse = "farmhouse"
    independent_house = "independent_house"


class TransactionType(str, enum.Enum):
    buy = "buy"
    rent = "rent"


class SourcePortal(str, enum.Enum):
    ninetyacres = "99acres"
    magicbricks = "magicbricks"
    housing = "housing"
    nobroker = "nobroker"
    commonfloor = "commonfloor"
    squareyards = "squareyards"
    makaan = "makaan"
    manual = "manual"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    source_portal = Column(Enum(SourcePortal), nullable=False)
    listing_url = Column(Text, unique=True)
    title = Column(String(500))
    property_type = Column(Enum(PropertyType))
    transaction_type = Column(Enum(TransactionType), nullable=False)

    price = Column(Float)
    price_currency = Column(String(10), default="INR")
    area_sqft = Column(Float)

    # Location
    address = Column(Text)
    locality = Column(String(255))
    city = Column(String(100), default="Delhi")
    pincode = Column(String(10))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Owner contact (may be redundant with lead — kept for raw data integrity)
    owner_name = Column(String(255))
    owner_phone = Column(String(20))
    owner_email = Column(String(255))
    owner_whatsapp = Column(String(20))

    listing_date = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_duplicate = Column(Boolean, default=False)

    # Tags
    budget_range = Column(String(50))  # e.g. "1Cr-2Cr"
    location_tag = Column(String(100))  # e.g. "prime_south_delhi"

    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    lead = relationship("Lead", back_populates="properties")

    created_at = Column(DateTime, default=datetime.utcnow)
