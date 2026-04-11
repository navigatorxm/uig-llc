from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lead import Lead, PipelineStage
from app.models.outreach_log import OutreachLog, OutreachChannel
from app.schemas.outreach import OutreachSendRequest, OutreachSendResponse
from app.services.outreach.whatsapp import WhatsAppService
from app.services.outreach.email import EmailService
from app.services.outreach.templates import render_template
from datetime import datetime, timezone
from app.auth.jwt import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/outreach/send", response_model=OutreachSendResponse)
def send_outreach(request: OutreachSendRequest, db: Session = Depends(get_db)):
    """Manually trigger outreach to a lead on a specific channel."""
    lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    prop = lead.properties[0] if lead.properties else None
    context = {
        "owner_name": lead.owner_name,
        "property_address": prop.locality if prop else "your property",
        "transaction_type": prop.transaction_type.value if prop else "buy",
    }

    log = OutreachLog(
        lead_id=lead.id,
        channel=request.channel,
        message_template=request.template,
    )

    if request.channel == OutreachChannel.whatsapp:
        if not lead.whatsapp:
            raise HTTPException(status_code=400, detail="Lead has no WhatsApp number")
        msg = request.custom_message or render_template(request.template, context)
        result = WhatsAppService().send(lead.whatsapp, msg)
        log.message_body = msg
        log.delivery_sid = result.get("sid")
        status = result.get("status", "sent")

    elif request.channel == OutreachChannel.email:
        if not lead.email:
            raise HTTPException(status_code=400, detail="Lead has no email address")
        subject, body = render_template(request.template, context, email=True)
        result = EmailService().send(lead.email, lead.owner_name, subject, body)
        log.message_body = body
        log.delivery_sid = result.get("message_id")
        status = str(result.get("status", "sent"))

    else:
        raise HTTPException(status_code=400, detail="Unsupported channel")

    db.add(log)

    # Update lead tracking fields
    if not lead.first_contact_at:
        lead.first_contact_at = datetime.now(timezone.utc)
        lead.pipeline_stage = PipelineStage.contact_initiated
    lead.last_contact_at = datetime.now(timezone.utc)
    lead.contact_attempt_count += 1

    db.commit()
    db.refresh(log)

    return OutreachSendResponse(
        log_id=log.id,
        lead_id=lead.id,
        channel=request.channel.value,
        status=status,
        message="Outreach sent successfully",
    )
