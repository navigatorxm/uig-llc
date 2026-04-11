"""Admin pipeline router — extended lead analytics and conversion tracking."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional
from app.database import get_db
from app.models.lead import Lead, PipelineStage
from app.models.property import Property
from app.models.deal import Deal, DealStatus
from app.models.outreach_log import OutreachLog, OutreachChannel
from app.models.agent import Agent
from app.models.lpi_certificate import LPICertificateRecord
from app.routers.admin_auth import get_admin_user

router = APIRouter(
    prefix="/api/admin/pipeline",
    tags=["Admin Pipeline"],
    dependencies=[Depends(get_admin_user)],
)


@router.get("/overview")
def pipeline_overview(db: Session = Depends(get_db)):
    """Comprehensive pipeline metrics for the business dashboard."""
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Lead counts
    total_leads = db.query(func.count(Lead.id)).scalar()
    leads_today = db.query(func.count(Lead.id)).filter(Lead.created_at >= today).scalar()
    leads_this_week = db.query(func.count(Lead.id)).filter(Lead.created_at >= week_ago).scalar()
    leads_this_month = db.query(func.count(Lead.id)).filter(Lead.created_at >= month_ago).scalar()

    # Stage breakdown
    stage_counts = {}
    for stage in PipelineStage:
        count = db.query(func.count(Lead.id)).filter(Lead.pipeline_stage == stage).scalar()
        stage_counts[stage.value] = count

    # Conversion metrics
    responded = db.query(func.count(Lead.id)).filter(Lead.response_received == True).scalar()
    interested = db.query(func.count(Lead.id)).filter(Lead.interested == True).scalar()
    closed_won = stage_counts.get("closed_won", 0)
    closed_lost = stage_counts.get("closed_lost", 0)

    # Outreach stats
    total_outreach = db.query(func.count(OutreachLog.id)).scalar()
    outreach_week = db.query(func.count(OutreachLog.id)).filter(OutreachLog.sent_at >= week_ago).scalar()

    # Properties & deals
    total_properties = db.query(func.count(Property.id)).scalar()
    active_deals = db.query(func.count(Deal.id)).filter(Deal.status == DealStatus.pending).scalar()
    pipeline_value = (
        db.query(func.coalesce(func.sum(Deal.agreed_price), 0))
        .filter(Deal.status == DealStatus.pending)
        .scalar()
    )

    # Agent network
    total_agents = db.query(func.count(Agent.id)).scalar()
    active_agents = db.query(func.count(Agent.id)).filter(Agent.lpi_license_active == True).scalar()

    # LPI certificates
    total_certs = db.query(func.count(LPICertificateRecord.id)).scalar()

    return {
        "leads": {
            "total": total_leads,
            "today": leads_today,
            "this_week": leads_this_week,
            "this_month": leads_this_month,
        },
        "pipeline_stages": stage_counts,
        "conversion": {
            "response_rate": round((responded / total_leads * 100), 1) if total_leads else 0,
            "interest_rate": round((interested / total_leads * 100), 1) if total_leads else 0,
            "win_rate": round((closed_won / total_leads * 100), 1) if total_leads else 0,
            "responded": responded,
            "interested": interested,
            "closed_won": closed_won,
            "closed_lost": closed_lost,
        },
        "outreach": {
            "total_sent": total_outreach,
            "sent_this_week": outreach_week,
        },
        "properties": {
            "total_scraped": total_properties,
        },
        "deals": {
            "active": active_deals,
            "pipeline_value_inr": pipeline_value,
        },
        "agents": {
            "total": total_agents,
            "active_licensed": active_agents,
        },
        "lpi": {
            "total_certificates": total_certs,
        },
    }


@router.get("/lead-velocity")
def lead_velocity(days: int = Query(default=30, le=90), db: Session = Depends(get_db)):
    """Daily lead acquisition rate for charts."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    daily = db.query(
        func.date(Lead.created_at).label("day"),
        func.count(Lead.id),
    ).filter(Lead.created_at >= cutoff).group_by(func.date(Lead.created_at)).all()

    return {
        "daily_leads": [
            {"date": str(day), "count": count}
            for day, count in daily
        ]
    }


@router.get("/conversion-funnel")
def conversion_funnel(db: Session = Depends(get_db)):
    """Full funnel with conversion rates between stages."""
    stages = list(PipelineStage)
    funnel = []
    prev_count = None

    for stage in stages:
        count = db.query(func.count(Lead.id)).filter(Lead.pipeline_stage == stage).scalar()
        drop_off = round(((prev_count - count) / prev_count * 100), 1) if prev_count and prev_count > 0 else 0
        funnel.append({
            "stage": stage.value,
            "count": count,
            "drop_off_pct": drop_off,
        })
        prev_count = count if count > 0 else prev_count

    return {"funnel": funnel}


@router.get("/top-leads")
def top_leads(limit: int = Query(default=20, le=50), db: Session = Depends(get_db)):
    """Top scored leads for priority follow-up."""
    leads = (
        db.query(Lead)
        .filter(Lead.pipeline_stage.notin_([PipelineStage.closed_won, PipelineStage.closed_lost]))
        .order_by(Lead.lead_score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": l.id,
            "owner_name": l.owner_name,
            "phone": l.phone,
            "email": l.email,
            "stage": l.pipeline_stage.value,
            "lead_score": l.lead_score,
            "response_received": l.response_received,
            "interested": l.interested,
            "contact_attempts": l.contact_attempt_count,
            "last_contact_at": l.last_contact_at.isoformat() if l.last_contact_at else None,
        }
        for l in leads
    ]
