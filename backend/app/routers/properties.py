from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.property import Property, TransactionType, SourcePortal
from app.schemas.property import PropertyResponse, ScrapeRequest, ScrapeResponse
from app.workers.scraping_tasks import scrape_portal

router = APIRouter()


@router.post("/scraping/trigger", response_model=ScrapeResponse)
def trigger_scrape(request: ScrapeRequest, db: Session = Depends(get_db)):
    """Kick off an async scraping job for a given portal."""
    task = scrape_portal.delay(
        portal=request.portal.value,
        location=request.location,
        transaction_type=request.transaction_type.value,
        property_type=request.property_type.value if request.property_type else None,
        max_pages=request.max_pages,
    )
    return ScrapeResponse(
        task_id=task.id,
        portal=request.portal.value,
        status="queued",
        message=f"Scraping job queued for {request.portal.value} — {request.location}",
    )


@router.get("/scraping/status/{task_id}")
def scrape_status(task_id: str):
    """Check the status of a scraping task."""
    from app.workers.celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@router.get("/properties", response_model=List[PropertyResponse])
def list_properties(
    portal: Optional[SourcePortal] = None,
    transaction_type: Optional[TransactionType] = None,
    city: Optional[str] = None,
    locality: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_duplicate: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Property).filter(Property.is_duplicate == is_duplicate)

    if portal:
        query = query.filter(Property.source_portal == portal)
    if transaction_type:
        query = query.filter(Property.transaction_type == transaction_type)
    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if locality:
        query = query.filter(Property.locality.ilike(f"%{locality}%"))
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)

    return query.order_by(Property.scraped_at.desc()).offset(skip).limit(limit).all()


@router.get("/properties/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop
