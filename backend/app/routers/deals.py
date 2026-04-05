from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.deal import Deal, DealStatus
from app.models.lead import Lead, PipelineStage
from app.schemas.deal import DealCreate, DealUpdate, DealResponse

router = APIRouter()


@router.get("/deals", response_model=List[DealResponse])
def list_deals(
    status: DealStatus = None,
    db: Session = Depends(get_db),
):
    query = db.query(Deal)
    if status:
        query = query.filter(Deal.status == status)
    return query.order_by(Deal.created_at.desc()).all()


@router.post("/deals", response_model=DealResponse, status_code=201)
def create_deal(deal_in: DealCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == deal_in.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    deal = Deal(**deal_in.model_dump())
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.get("/deals/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.patch("/deals/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: int, updates: DealUpdate, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)

    deal.updated_at = datetime.utcnow()

    # Sync lead stage based on deal status
    if updates.status == DealStatus.approved:
        deal.lead.pipeline_stage = PipelineStage.approved
    elif updates.status == DealStatus.rejected:
        deal.lead.pipeline_stage = PipelineStage.closed_lost
    elif updates.site_visit_scheduled_at:
        deal.lead.pipeline_stage = PipelineStage.visit_scheduled
    elif updates.agreement_signed_at and updates.payment_completed_at:
        deal.lead.pipeline_stage = PipelineStage.closed_won

    db.commit()
    db.refresh(deal)
    return deal
