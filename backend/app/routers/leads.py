from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timezone
from app.database import get_db
from app.models.lead import Lead, PipelineStage
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStageUpdate, LeadResponse, LeadScoreResponse
from app.services.ai.lead_scorer import LeadScorer
from app.services.crm.hubspot import HubSpotService
from app.auth.jwt import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/leads", response_model=List[LeadResponse])
def list_leads(
    stage: Optional[PipelineStage] = None,
    interested: Optional[bool] = None,
    min_score: Optional[float] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Lead)
    if stage:
        query = query.filter(Lead.pipeline_stage == stage)
    if interested is not None:
        query = query.filter(Lead.interested == interested)
    if min_score is not None:
        query = query.filter(Lead.lead_score >= min_score)
    return query.order_by(Lead.lead_score.desc(), Lead.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/leads", response_model=LeadResponse, status_code=201)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**lead_in.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Auto-score and sync to HubSpot
    _score_and_sync(lead, db)
    return lead


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, updates: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


@router.patch("/leads/{lead_id}/stage", response_model=LeadResponse)
def update_stage(lead_id: int, stage_update: LeadStageUpdate, db: Session = Depends(get_db)):
    """Advance a lead to a new pipeline stage with side effects."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_stage = lead.pipeline_stage
    lead.pipeline_stage = stage_update.stage
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()

    # Side effects based on stage transition
    _handle_stage_transition(lead, old_stage, stage_update.stage, db)

    db.refresh(lead)
    return lead


@router.get("/leads/{lead_id}/score", response_model=LeadScoreResponse)
def get_lead_score(lead_id: int, db: Session = Depends(get_db)):
    """Compute or retrieve AI lead score."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Use cached score if available
    if lead.lead_score_breakdown:
        try:
            breakdown_data = json.loads(lead.lead_score_breakdown)
            return LeadScoreResponse(
                lead_id=lead_id,
                score=lead.lead_score,
                breakdown=breakdown_data.get("breakdown", {}),
                priority=breakdown_data.get("priority", "medium"),
                reasoning=breakdown_data.get("reasoning", ""),
            )
        except json.JSONDecodeError:
            pass

    # Recompute
    return _score_lead(lead, db)


def _score_and_sync(lead: Lead, db: Session):
    """Score a lead with AI and sync to HubSpot."""
    try:
        _score_lead(lead, db)
    except Exception:
        pass
    try:
        hs = HubSpotService()
        contact_id = hs.create_or_update_contact(lead)
        if contact_id and not lead.hubspot_contact_id:
            lead.hubspot_contact_id = contact_id
            db.commit()
    except Exception:
        pass


def _score_lead(lead: Lead, db: Session) -> LeadScoreResponse:
    prop = lead.properties[0] if lead.properties else None
    lead_data = {
        "owner_name": lead.owner_name,
        "phone": lead.phone,
        "email": lead.email,
        "whatsapp": lead.whatsapp,
        "pipeline_stage": lead.pipeline_stage.value,
        "response_received": lead.response_received,
        "location_tag": prop.location_tag if prop else None,
        "listing_date": prop.listing_date.isoformat() if prop and prop.listing_date else None,
        "price": prop.price if prop else None,
    }

    scorer = LeadScorer()
    result = scorer.score(lead_data)

    lead.lead_score = result.get("score", 0)
    import json as _json
    lead.lead_score_breakdown = _json.dumps(result)
    db.commit()

    return LeadScoreResponse(
        lead_id=lead.id,
        score=result.get("score", 0),
        breakdown=result.get("breakdown", {}),
        priority=result.get("priority", "medium"),
        reasoning=result.get("reasoning", ""),
    )


def _handle_stage_transition(lead: Lead, _old_stage: PipelineStage, new_stage: PipelineStage, db: Session):
    """Trigger automation when a lead moves to a new pipeline stage."""
    from app.workers.outreach_tasks import send_document_request

    if new_stage == PipelineStage.qualified:
        # Chain 2 T+0: Auto-request documents on qualification
        prop = lead.properties[0] if lead.properties else None
        tx_type = prop.transaction_type.value if prop else "buy"
        send_document_request.delay(lead.id, tx_type)

    elif new_stage == PipelineStage.approved:
        # Chain 3 T+0: Notify team + create HubSpot deal
        from app.services.crm.hubspot import HubSpotService
        from app.services.outreach.whatsapp import WhatsAppService
        from app.services.outreach.templates import render_template
        from app.services.outreach.email import EmailService

        hs = HubSpotService()
        prop = lead.properties[0] if lead.properties else None
        deal_type = prop.transaction_type.value if prop else "buy"
        deal_id = hs.create_deal(lead, prop, deal_type)
        if deal_id:
            from app.models.deal import Deal
            deal = db.query(Deal).filter(Deal.lead_id == lead.id).first()
            if deal:
                deal.hubspot_deal_id = deal_id
                db.commit()

        # Send approval notification to lead
        if lead.whatsapp:
            context = {
                "owner_name": lead.owner_name,
                "property_address": prop.locality if prop else "your property",
                "transaction_type": deal_type,
            }
            try:
                msg = render_template("approval_notification_whatsapp", context)
                WhatsAppService().send(lead.whatsapp, msg)
            except Exception:
                pass
        if lead.email:
            context = {
                "owner_name": lead.owner_name,
                "property_address": prop.locality if prop else "your property",
                "transaction_type": deal_type,
            }
            try:
                subject, body = render_template("approval_email", context, email=True)
                EmailService().send(lead.email, lead.owner_name, subject, body)
            except Exception:
                pass

    elif new_stage == PipelineStage.closed_lost:
        # Send polite decline via WhatsApp
        from app.services.outreach.whatsapp import WhatsAppService
        from app.services.outreach.templates import render_template
        if lead.whatsapp:
            prop = lead.properties[0] if lead.properties else None
            context = {
                "owner_name": lead.owner_name,
                "property_address": prop.locality if prop else "your property",
                "transaction_type": prop.transaction_type.value if prop else "buy",
                "rejection_reason": "internal acquisition criteria",
            }
            try:
                msg = render_template("rejection_notification_whatsapp", context)
                WhatsAppService().send(lead.whatsapp, msg)
            except Exception:
                pass

    elif new_stage == PipelineStage.cold_lead:
        # Log that the lead has been moved to cold status after 72h
        from app.models.outreach_log import OutreachLog, OutreachChannel
        db.add(OutreachLog(
            lead_id=lead.id,
            channel=OutreachChannel.email,
            message_template="cold_lead_auto_classification",
            message_body="Lead automatically classified as cold after 72h with no response across 5 follow-ups.",
        ))
        db.commit()

    elif new_stage == PipelineStage.pending_docs:
        # Notify team about stalled doc collection
        from app.services.outreach.email import EmailService
        es = EmailService()
        es.send_internal(
            subject=f"Pending Docs Alert — {lead.owner_name} (Lead #{lead.id})",
            body=f"Lead {lead.id} ({lead.owner_name}) has not completed document submission after 14 days. "
                 f"Consider manual follow-up or re-allocation.",
        )
