from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.lead import PipelineStage


class LeadBase(BaseModel):
    owner_name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    pipeline_stage: Optional[PipelineStage] = None
    interested: Optional[bool] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class LeadStageUpdate(BaseModel):
    stage: PipelineStage


class LeadResponse(LeadBase):
    id: int
    pipeline_stage: PipelineStage
    lead_score: float
    hubspot_contact_id: Optional[str] = None
    first_contact_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    contact_attempt_count: int
    response_received: bool
    interested: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadScoreResponse(BaseModel):
    lead_id: int
    score: float
    breakdown: dict
    priority: str  # "high" | "medium" | "low"
    reasoning: str
