"""Celery tasks for automated outreach and follow-ups.

Three-chain communication pipeline:
  Chain 1 — Initial outreach + 5 follow-ups within 48h, cold-lead cutoff at 72h
  Chain 2 — Document collection (triggered on qualified), pending-docs cutoff at 14 days
  Chain 3 — Verification outcome (triggered when all docs received)
"""
import logging
from datetime import datetime, timedelta
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.lead import Lead, PipelineStage
from app.models.outreach_log import OutreachLog, OutreachChannel
from app.services.outreach.pipeline_config import (
    CHAIN1_FU1, CHAIN1_FU2, CHAIN1_FU3, CHAIN1_FU4, CHAIN1_FU5, CHAIN1_COLD_LEAD_CUTOFF,
    CHAIN2_DOC_FU1, CHAIN2_DOC_FU2, CHAIN2_DOC_FU3, CHAIN2_PENDING_DOCS_CUTOFF,
)

logger = logging.getLogger(__name__)


@celery_app.task
def send_initial_outreach(lead_id: int):
    """Chain 1 T+0: Send initial WhatsApp + email to a new lead."""
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
        city_or_area = prop.locality if prop else "your area"
        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": prop.transaction_type.value if prop else "buy",
            "city_or_area": city_or_area,
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
        logger.info(f"Chain 1 T+0: Initial outreach sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Outreach failed for lead {lead_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def process_follow_ups():
    """
    Check for leads that need follow-ups across all chains.
    Runs every 6 hours via Celery Beat.

    Chain 1 — 5 follow-ups at 8h, 16h, 24h, 36h, 48h; cold_lead at 72h
    Chain 2 — doc follow-ups at 48h, 120h, 240h; pending_docs at 336h (14 days)
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # ── CHAIN 1: Initial outreach follow-ups ──
        # Follow-up #1 at T+8h
        fu1_cutoff = now - timedelta(minutes=CHAIN1_FU1)
        needs_fu1 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= fu1_cutoff,
                Lead.contact_attempt_count == 1,
            )
            .all()
        )
        for lead in needs_fu1:
            send_follow_up.delay(lead.id, follow_up_number=1)

        # Follow-up #2 at T+16h
        fu2_cutoff = now - timedelta(minutes=CHAIN1_FU2)
        needs_fu2 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= fu2_cutoff,
                Lead.contact_attempt_count == 2,
            )
            .all()
        )
        for lead in needs_fu2:
            send_follow_up.delay(lead.id, follow_up_number=2)

        # Follow-up #3 at T+24h
        fu3_cutoff = now - timedelta(minutes=CHAIN1_FU3)
        needs_fu3 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= fu3_cutoff,
                Lead.contact_attempt_count == 3,
            )
            .all()
        )
        for lead in needs_fu3:
            send_follow_up.delay(lead.id, follow_up_number=3)

        # Follow-up #4 at T+36h
        fu4_cutoff = now - timedelta(minutes=CHAIN1_FU4)
        needs_fu4 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= fu4_cutoff,
                Lead.contact_attempt_count == 4,
            )
            .all()
        )
        for lead in needs_fu4:
            send_follow_up.delay(lead.id, follow_up_number=4)

        # Follow-up #5 (final) at T+48h
        fu5_cutoff = now - timedelta(minutes=CHAIN1_FU5)
        needs_fu5 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= fu5_cutoff,
                Lead.contact_attempt_count == 5,
            )
            .all()
        )
        for lead in needs_fu5:
            send_follow_up.delay(lead.id, follow_up_number=5)

        # Cold lead cutoff at T+72h
        cold_cutoff = now - timedelta(minutes=CHAIN1_COLD_LEAD_CUTOFF)
        cold_leads = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.contact_initiated,
                Lead.response_received == False,
                Lead.last_contact_at <= cold_cutoff,
                Lead.contact_attempt_count >= 6,
            )
            .all()
        )
        for lead in cold_leads:
            lead.pipeline_stage = PipelineStage.cold_lead
            logger.info(f"Lead {lead.id} moved to cold_lead (72h no response)")

        # ── CHAIN 2: Document collection follow-ups ──
        # Doc follow-up #1 at T+48h
        doc_fu1_cutoff = now - timedelta(minutes=CHAIN2_DOC_FU1)
        needs_doc_fu1 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.docs_requested,
                Lead.last_contact_at <= doc_fu1_cutoff,
                Lead.contact_attempt_count == 1,
            )
            .all()
        )
        for lead in needs_doc_fu1:
            send_doc_follow_up.delay(lead.id, follow_up_number=1)

        # Doc follow-up #2 at T+120h (5 days)
        doc_fu2_cutoff = now - timedelta(minutes=CHAIN2_DOC_FU2)
        needs_doc_fu2 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.docs_requested,
                Lead.last_contact_at <= doc_fu2_cutoff,
                Lead.contact_attempt_count == 2,
            )
            .all()
        )
        for lead in needs_doc_fu2:
            send_doc_follow_up.delay(lead.id, follow_up_number=2)

        # Doc follow-up #3 (final) at T+240h (10 days)
        doc_fu3_cutoff = now - timedelta(minutes=CHAIN2_DOC_FU3)
        needs_doc_fu3 = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.docs_requested,
                Lead.last_contact_at <= doc_fu3_cutoff,
                Lead.contact_attempt_count == 3,
            )
            .all()
        )
        for lead in needs_doc_fu3:
            send_doc_follow_up.delay(lead.id, follow_up_number=3)

        # Pending docs cutoff at T+336h (14 days)
        pending_docs_cutoff = now - timedelta(minutes=CHAIN2_PENDING_DOCS_CUTOFF)
        pending_docs_leads = (
            db.query(Lead)
            .filter(
                Lead.pipeline_stage == PipelineStage.docs_requested,
                Lead.last_contact_at <= pending_docs_cutoff,
                Lead.contact_attempt_count >= 4,
            )
            .all()
        )
        for lead in pending_docs_leads:
            lead.pipeline_stage = PipelineStage.pending_docs
            logger.info(f"Lead {lead.id} moved to pending_docs (14 days incomplete)")

        logger.info(
            f"Follow-up dispatch: "
            f"Chain1: {len(needs_fu1)} FU1, {len(needs_fu2)} FU2, "
            f"{len(needs_fu3)} FU3, {len(needs_fu4)} FU4, {len(needs_fu5)} FU5, "
            f"{len(cold_leads)} cold_lead | "
            f"Chain2: {len(needs_doc_fu1)} doc-FU1, {len(needs_doc_fu2)} doc-FU2, "
            f"{len(needs_doc_fu3)} doc-FU3, {len(pending_docs_leads)} pending_docs"
        )
    finally:
        db.close()


@celery_app.task
def send_follow_up(lead_id: int, follow_up_number: int):
    """Send a numbered follow-up message (Chain 1: 1-5 within 48h)."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.templates import render_template

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        prop = lead.properties[0] if lead.properties else None
        city_or_area = prop.locality if prop else "your area"
        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": prop.transaction_type.value if prop else "buy",
            "city_or_area": city_or_area,
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
        logger.info(f"Chain 1 FU#{follow_up_number} sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Follow-up #{follow_up_number} failed for lead {lead_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def send_doc_follow_up(lead_id: int, follow_up_number: int):
    """Send a document collection follow-up (Chain 2: 1-3 over 10 days)."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.templates import render_template, get_doc_checklist
    from app.models.document import PURCHASE_REQUIRED_DOCS

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        prop = lead.properties[0] if lead.properties else None
        location_tag = prop.location_tag if prop else None

        # Build missing docs list
        all_docs = PURCHASE_REQUIRED_DOCS
        # For now, send generic follow-up; in production you'd track which docs are received
        missing_docs = "Please share the pending documents at your earliest convenience."
        docs_received_count = 0
        docs_total_count = len(all_docs)

        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": prop.transaction_type.value if prop else "buy",
            "missing_docs": missing_docs,
            "docs_received_count": docs_received_count,
            "docs_total_count": docs_total_count,
        }

        template_key = f"doc_follow_up_{follow_up_number}_whatsapp"

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
        logger.info(f"Chain 2 Doc-FU#{follow_up_number} sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Doc follow-up #{follow_up_number} failed for lead {lead_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def send_document_request(lead_id: int, transaction_type: str = "buy"):
    """Chain 2 T+0: Send document request checklist to a qualified lead."""
    from app.services.outreach.whatsapp import WhatsAppService
    from app.services.outreach.email import EmailService
    from app.services.outreach.templates import render_template, get_doc_checklist
    from app.models.document import PURCHASE_REQUIRED_DOCS, RENTAL_REQUIRED_DOCS

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        prop = lead.properties[0] if lead.properties else None
        location_tag = prop.location_tag if prop else None

        # Use state-specific checklist if available, otherwise fall back to generic
        if location_tag:
            doc_list = get_doc_checklist(location_tag, transaction_type)
        else:
            required = PURCHASE_REQUIRED_DOCS if transaction_type == "buy" else RENTAL_REQUIRED_DOCS
            doc_list = "\n".join(f"• {d.value.replace('_', ' ').title()}" for d in required)

        context = {
            "owner_name": lead.owner_name,
            "property_address": prop.locality if prop else "your property",
            "transaction_type": transaction_type,
            "doc_list": doc_list,
        }

        # Send WhatsApp
        msg = render_template("document_request_whatsapp", context)
        if lead.whatsapp:
            WhatsAppService().send(lead.whatsapp, msg)
            db.add(OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.whatsapp,
                message_template="document_request_whatsapp",
                message_body=msg,
            ))

        # Send email
        if lead.email:
            subject, body = render_template("document_request_email", context, email=True)
            EmailService().send(lead.email, lead.owner_name, subject, body)
            db.add(OutreachLog(
                lead_id=lead_id,
                channel=OutreachChannel.email,
                message_template="document_request_email",
                message_body=body,
            ))

        lead.pipeline_stage = PipelineStage.docs_requested
        lead.last_contact_at = datetime.utcnow()
        lead.contact_attempt_count = 0  # Reset for doc chain tracking
        db.commit()

        logger.info(f"Chain 2 T+0: Doc request sent to lead {lead_id}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Doc request failed for lead {lead_id}: {exc}")
    finally:
        db.close()
