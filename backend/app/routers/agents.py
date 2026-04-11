"""API router for real estate agent partner management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.agent import Agent, AgentStatus, AgentTier
from app.services.agents.agent_outreach import (
    generate_city_agent_campaign_brief,
    AgentOutreachService,
)
from app.auth.jwt import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/agents", response_model=List[dict])
def list_agents(
    city: Optional[str] = None,
    status: Optional[AgentStatus] = None,
    tier: Optional[AgentTier] = None,
    lpi_licensed: Optional[bool] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Agent)
    if city:
        query = query.filter(Agent.city == city)
    if status:
        query = query.filter(Agent.status == status)
    if tier:
        query = query.filter(Agent.tier == tier)
    if lpi_licensed is not None:
        query = query.filter(Agent.lpi_license_active == lpi_licensed)
    return [
        {
            "id": a.id, "full_name": a.full_name, "agency_name": a.agency_name,
            "city": a.city, "phone": a.phone, "email": a.email,
            "tier": a.tier, "status": a.status,
            "lpi_license_active": a.lpi_license_active,
            "total_referrals": a.total_referrals,
            "successful_conversions": a.successful_conversions,
        }
        for a in query.offset(skip).limit(limit).all()
    ]


@router.post("/agents", status_code=201)
def create_agent(agent_data: dict, db: Session = Depends(get_db)):
    """Add a new agent prospect to the CRM."""
    agent = Agent(**agent_data)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"id": agent.id, "message": "Agent created", "status": agent.status}


@router.get("/agents/{agent_id}")
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/agents/{agent_id}/pitch")
def send_partnership_pitch(agent_id: int, db: Session = Depends(get_db)):
    """Send the initial UIG partnership pitch to an agent."""
    agent_rec = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent_rec:
        raise HTTPException(status_code=404, detail="Agent not found")

    from app.services.agents.agent_crm import AgentProfile, AgentSpecialization
    agent_profile = AgentProfile(
        id=agent_rec.id,
        full_name=agent_rec.full_name,
        agency_name=agent_rec.agency_name or "",
        city=agent_rec.city,
        state=agent_rec.state or "",
        phone=agent_rec.phone or "",
        email=agent_rec.email or "",
        whatsapp=agent_rec.whatsapp or agent_rec.phone or "",
        rera_number=agent_rec.rera_number or "",
    )

    svc = AgentOutreachService()
    result = svc.send_initial_pitch(agent_profile)

    agent_rec.status = AgentStatus.pitched
    agent_rec.first_contact_at = agent_rec.first_contact_at or datetime.utcnow()
    agent_rec.last_contact_at = datetime.utcnow()
    agent_rec.contact_attempts += 1
    db.commit()

    return {"agent_id": agent_id, "result": result, "status": "pitched"}


@router.post("/agents/{agent_id}/onboard")
def onboard_agent(agent_id: int, db: Session = Depends(get_db)):
    """Onboard an agent — activate LPI license and send welcome message."""
    from datetime import timedelta
    agent_rec = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent_rec:
        raise HTTPException(status_code=404, detail="Agent not found")

    now = datetime.utcnow()
    agent_rec.status = AgentStatus.onboarded
    agent_rec.lpi_license_active = True
    agent_rec.lpi_license_issued_at = now
    agent_rec.lpi_license_expiry = now.replace(year=now.year + 1)
    db.commit()

    return {
        "agent_id": agent_id,
        "message": "Agent onboarded",
        "lpi_license_active": True,
        "license_expiry": agent_rec.lpi_license_expiry.isoformat(),
    }


@router.get("/agents/campaign/{city}")
def get_city_campaign_brief(city: str):
    """Get the full agent acquisition campaign brief for a city."""
    return generate_city_agent_campaign_brief(city)


@router.get("/agents/cities/all")
def list_all_target_cities():
    """Return all cities and their airport zone data."""
    from app.data.airports import AIRPORTS
    return [
        {
            "city": a.city,
            "state": a.state,
            "airport": a.airport_name,
            "iata": a.iata_code,
            "tier": a.tier,
            "priority_rank": a.priority_rank,
            "avg_price_sqft": a.avg_price_per_sqft_inr,
            "lpi_coverage_pct": a.lpi_coverage_pct,
        }
        for a in sorted(AIRPORTS, key=lambda x: x.priority_rank)
    ]
