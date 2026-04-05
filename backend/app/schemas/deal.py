from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.deal import DealType, DealStatus


class DealCreate(BaseModel):
    lead_id: int
    property_id: Optional[int] = None
    deal_type: DealType
    agreed_price: Optional[float] = None
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    status: Optional[DealStatus] = None
    agreed_price: Optional[float] = None
    site_visit_scheduled_at: Optional[datetime] = None
    agreement_signed_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None
    notes: Optional[str] = None


class DealResponse(BaseModel):
    id: int
    lead_id: int
    property_id: Optional[int] = None
    deal_type: DealType
    status: DealStatus
    agreed_price: Optional[float] = None
    price_currency: str
    hubspot_deal_id: Optional[str] = None
    site_visit_scheduled_at: Optional[datetime] = None
    agreement_signed_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
