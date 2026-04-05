"""Celery tasks for automated outreach and follow-ups."""
import logging
from datetime import datetime, timedelta
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.lead import Lead, PipelineStage
from app.models.outreach_log import OutreachLog, OutreachChannel

logger = logging.getLogger(__name__)


@celery_app.task
def send_initial_outreach(lead_id: int):
    """Send initial WhatsApp + email to a new lead."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.email import EmailService
    from app.services.outreach.templates import render_template

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            logger.warning(f"Lead {lead_id} not found")
            return

        whatsapp_svc = WhatsAppService()
        email_svc = EmailService()

        # Get first property for context
        prop = lead.properties[0] if lead.properties else None
        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": prop.transaction_type.value if prop else "buy",
        }

        # Send WhatsApp
        if lead.whatsapp:
            msg = render_template("initial_contact_whatsapp", context)
            result = whatsapp_svc.send(lead.whatsapp, msg)
            log = OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.whatsapp,
                message_template="initial_contact_whatsapp",
                message_body=msg,
                delivery_sid=result.get("sid"),
            )
            db.add(log)

        # Send email
        if lead.email:
            subject, body = render_template("initial_contact_email", context, email=True)
            result = email_svc.send(lead.email, lead.owner_name, subject, body)
            log = OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.email,
                message_template="initial_contact_email",
                message_body=body,
                delivery_sid=result.get("message_id"),
            )
            db.add(log)

        # Advance stage
        lead.pipeline_stage = PipelineStage.contact_initiated
        lead.first_contact_at = datetime.utcnow()
        lead.last_contact_at = datetime.utcnow()
        lead.contact_attempt_count += 1

        db.commit()
        logger.info(f"Initial outreach sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Outreach failed for lead {lead_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def process_follow_ups():
    """Check for leads that need follow-up and dispatch tasks."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Leads with no response after 3 days → follow-up #1
        followup1_cutoff = now - timedelta(days=3)
        needs_followup1 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= followup1_cutoff,
                Lead.contact_attempt_count == 1,
            )
            .all()
        )

        for lead in needs_followup1:
            send_follow_up.delay(lead.id, follow_up_number=1)

        # Leads with no response after 7 days → follow-up #2
        followup2_cutoff = now - timedelta(days=7)
        needs_followup2 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= followup2_cutoff,
                Lead.contact_attempt_count == 2,
            )
            .all()
        )

        for lead in needs_followup2:
            send_follow_up.delay(lead.id, follow_up_number=2)

        logger.info(
            f"Follow-up dispatch: {len(needs_followup1)} follow-up#1, "
            f"{len(needs_followup2)} follow-up#2"
        )
    finally:
        db.close()


@celery_app.task
def send_follow_up(lead_id: int, follow_up_number: int):
    """Send a numbered follow-up message to a lead."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.email import EmailService
    from app.services.outreach.templates import render_template

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        prop = lead.properties[0] if lead.properties else None
        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": prop.transaction_type.value if prop else "buy",
            "follow_up_number": follow_up_number,
        }

        template_key = f"follow_up_{follow_up_number}_whatsapp"

        if lead.whatsapp:
            msg = render_template(template_key, context)
            WhatsAppService().send(lead.whatsapp, msg)
            db.add(OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.whatsapp,
                message_template=template_key,
                message_body=msg,
            ))

        lead.last_contact_at = datetime.utcnow()
        lead.contact_attempt_count += 1
        db.commit()
        logger.info(f"Follow-up #{follow_up_number} sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Follow-up failed for lead {lead_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def send_document_request(lead_id: int, transaction_type: str = "buy"):
    """Send document request checklist to a qualified lead."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.templates import render_template
    from app.models.document import PURCHASE_REQUIRED_DOCS, RENTAL_REQUIRED_DOCS

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        required = PURCHASE_REQUIRED_DOCS if transaction_type == "buy" else RENTAL_REQUIRED_DOCS
        doc_list = "\n".join(f"• {d.value.replace('_', ' ').title()}" for d in required)

        context = {
            "owner_name": lead.owner_name,
            "transaction_type": transaction_type,
            "doc_list": doc_list,
        }

        msg = render_template("document_request_whatsapp", context)

        if lead.whatsapp:
            WhatsAppService().send(lead.whatsapp, msg)
            db.add(OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.whatsapp,
                message_template="document_request_whatsapp",
                message_body=msg,
            ))

        lead.pipeline_stage = PipelineStage.docs_requested
        lead.last_contact_at = datetime.utcnow()
        db.commit()

    except Exception as exc:
        db.rollback()
        logger.error(f"Doc request failed for lead {lead_id}: {exc}")
    finally:
        db.close()
