from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models.lead import Lead, PipelineStage
from app.models.property import Property
from app.models.deal import Deal, DealStatus
from app.models.outreach_log import OutreachLog

router = APIRouter()


@router.get("/analytics/overview")
def get_overview(db: Session = Depends(get_db)):
    """Key performance indicators for the acquisition pipeline."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0)
    week_ago = now - timedelta(days=7)

    total_leads = db.query(func.count(Lead.id)).scalar()
    leads_today = db.query(func.count(Lead.id)).filter(Lead.created_at >= today_start).scalar()
    leads_this_week = db.query(func.count(Lead.id)).filter(Lead.created_at >= week_ago).scalar()

    responded = db.query(func.count(Lead.id)).filter(Lead.response_received == True).scalar()
    response_rate = round((responded / total_leads * 100), 1) if total_leads else 0

    qualified = db.query(func.count(Lead.id)).filter(
        Lead.pipeline_stage.in_([
            PipelineStage.qualified,
            PipelineStage.docs_requested,
            PipelineStage.docs_received,
            PipelineStage.under_verification,
            PipelineStage.approved,
            PipelineStage.visit_scheduled,
            PipelineStage.closed_won,
        ])
    ).scalar()
    qualification_rate = round((qualified / total_leads * 100), 1) if total_leads else 0

    closed_won = db.query(func.count(Lead.id)).filter(
        Lead.pipeline_stage == PipelineStage.closed_won
    ).scalar()
    conversion_rate = round((closed_won / total_leads * 100), 1) if total_leads else 0

    total_properties = db.query(func.count(Property.id)).scalar()
    active_deals = db.query(func.count(Deal.id)).filter(
        Deal.status == DealStatus.pending
    ).scalar()

    pipeline_value = (
        db.query(func.sum(Property.price))
        .join(Lead, Property.lead_id == Lead.id)
        .filter(
            Lead.pipeline_stage.in_([
                PipelineStage.qualified,
                PipelineStage.under_verification,
                PipelineStage.approved,
            ])
        )
        .scalar() or 0
    )

    return {
        "leads": {
            "total": total_leads,
            "today": leads_today,
            "this_week": leads_this_week,
        },
        "rates": {
            "response_rate_pct": response_rate,
            "qualification_rate_pct": qualification_rate,
            "conversion_rate_pct": conversion_rate,
        },
        "pipeline": {
            "total_properties_scraped": total_properties,
            "active_deals": active_deals,
            "deals_closed_won": closed_won,
            "pipeline_value_inr": pipeline_value,
        },
    }


@router.get("/analytics/funnel")
def get_funnel(db: Session = Depends(get_db)):
    """Stage-by-stage conversion funnel data."""
    funnel = []
    for stage in PipelineStage:
        count = db.query(func.count(Lead.id)).filter(Lead.pipeline_stage == stage).scalar()
        funnel.append({"stage": stage.value, "count": count})
    return {"funnel": funnel}


@router.get("/analytics/outreach")
def get_outreach_stats(db: Session = Depends(get_db)):
    """Outreach channel performance stats."""
    from app.models.outreach_log import OutreachChannel
    from sqlalchemy import case

    total = db.query(func.count(OutreachLog.id)).scalar()
    whatsapp_count = db.query(func.count(OutreachLog.id)).filter(
        OutreachLog.channel == OutreachChannel.whatsapp
    ).scalar()
    email_count = db.query(func.count(OutreachLog.id)).filter(
        OutreachLog.channel == OutreachChannel.email
    ).scalar()

    return {
        "total_messages_sent": total,
        "whatsapp": whatsapp_count,
        "email": email_count,
    }
