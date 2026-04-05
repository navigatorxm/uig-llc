from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.outreach_log import OutreachChannel


class OutreachSendRequest(BaseModel):
    lead_id: int
    channel: OutreachChannel
    template: str = "initial_contact"
    custom_message: Optional[str] = None


class OutreachSendResponse(BaseModel):
    log_id: int
    lead_id: int
    channel: str
    status: str
    message: str


class OutreachLogResponse(BaseModel):
    id: int
    lead_id: int
    channel: OutreachChannel
    message_template: Optional[str] = None
    sent_at: datetime
    delivered: Optional[bool] = None
    response_text: Optional[str] = None
    response_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
