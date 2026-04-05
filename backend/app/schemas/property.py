from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.property import PropertyType, TransactionType, SourcePortal


class PropertyBase(BaseModel):
    source_portal: SourcePortal
    listing_url: Optional[str] = None
    title: Optional[str] = None
    property_type: Optional[PropertyType] = None
    transaction_type: TransactionType
    price: Optional[float] = None
    area_sqft: Optional[float] = None
    address: Optional[str] = None
    locality: Optional[str] = None
    city: str = "Delhi"
    pincode: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    listing_date: Optional[datetime] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyResponse(PropertyBase):
    id: int
    is_duplicate: bool
    scraped_at: datetime
    budget_range: Optional[str] = None
    location_tag: Optional[str] = None
    lead_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScrapeRequest(BaseModel):
    portal: SourcePortal
    location: str = "Delhi NCR"
    transaction_type: TransactionType = TransactionType.buy
    property_type: Optional[PropertyType] = None
    max_pages: int = Field(default=5, ge=1, le=50)


class ScrapeResponse(BaseModel):
    task_id: str
    portal: str
    status: str
    message: str
