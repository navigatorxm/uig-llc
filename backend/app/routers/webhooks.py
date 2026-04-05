"""Inbound webhook handlers — WhatsApp replies, HubSpot events, Make.com."""
import logging
from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.lead import Lead, PipelineStage
from app.models.outreach_log import OutreachLog, OutreachChannel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive inbound WhatsApp messages from Twilio.
    Twilio sends form-encoded data with 'From' and 'Body' fields.
    """
    form = await request.form()
    from_number = str(form.get("From", "")).replace("whatsapp:", "")
    body = str(form.get("Body", "")).strip()

    logger.info(f"WhatsApp inbound from {from_number}: {body[:100]}")

    # Match lead by WhatsApp number
    lead = db.query(Lead).filter(Lead.whatsapp == from_number).first()
    if not lead:
        # Try phone field
        lead = db.query(Lead).filter(Lead.phone == from_number).first()

    if lead:
        lead.response_received = True
        lead.last_contact_at = datetime.utcnow()

        # Basic intent detection
        body_lower = body.lower()
        if any(word in body_lower for word in ["interested", "yes", "sure", "proceed", "ok", "confirm"]):
            lead.interested = True
            if lead.pipeline_stage in (PipelineStage.contact_initiated, PipelineStage.response_received):
                lead.pipeline_stage = PipelineStage.qualified

        elif any(word in body_lower for word in ["no", "not interested", "sold", "cancel", "stop"]):
            lead.interested = False
            lead.pipeline_stage = PipelineStage.closed_lost

        else:
            lead.pipeline_stage = PipelineStage.response_received

        # Log the response
        last_log = (
            db.query(OutreachLog)
            .filter(OutreachLog.lead_id == lead.id, OutreachLog.channel == OutreachChannel.whatsapp)
            .order_by(OutreachLog.sent_at.desc())
            .first()
        )
        if last_log:
            last_log.response_text = body
            last_log.response_at = datetime.utcnow()

        db.commit()
        logger.info(f"Lead {lead.id} updated from WhatsApp reply — stage: {lead.pipeline_stage}")

    # Twilio expects a 200 TwiML response (empty is fine for one-way)
    return Response(content="<?xml version='1.0'?><Response></Response>", media_type="text/xml")


@router.post("/webhooks/hubspot")
async def hubspot_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle HubSpot CRM update events (contact stage changes, deal updates)."""
    try:
        payload = await request.json()
        logger.info(f"HubSpot webhook: {payload}")

        for event in payload if isinstance(payload, list) else [payload]:
            object_type = event.get("subscriptionType", "")
            if "contact" in object_type:
                hubspot_id = str(event.get("objectId", ""))
                lead = db.query(Lead).filter(Lead.hubspot_contact_id == hubspot_id).first()
                if lead:
                    # Sync any stage change from HubSpot back to our DB
                    new_stage = event.get("propertyValue")
                    if new_stage:
                        logger.info(f"HubSpot stage update for lead {lead.id}: {new_stage}")
                    db.commit()

    except Exception as exc:
        logger.error(f"HubSpot webhook error: {exc}")

    return {"status": "ok"}


@router.post("/webhooks/make")
async def make_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Make.com (Integromat) automation trigger events."""
    try:
        payload = await request.json()
        logger.info(f"Make.com webhook: {payload}")

        action = payload.get("action")
        lead_id = payload.get("lead_id")

        if action and lead_id:
            from app.workers.outreach_tasks import send_initial_outreach, send_document_request
            if action == "send_initial_outreach":
                send_initial_outreach.delay(lead_id)
            elif action == "send_document_request":
                transaction_type = payload.get("transaction_type", "buy")
                send_document_request.delay(lead_id, transaction_type)

    except Exception as exc:
        logger.error(f"Make webhook error: {exc}")

    return {"status": "ok"}
