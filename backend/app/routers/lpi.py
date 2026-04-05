"""API router for LPI certificate issuance, lookup, and verification."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.lpi.certifier import (
    generate_lpi_code, issue_certificate, verify_lpi_code
)
from app.services.geofencing import (
    find_airport_zones, is_in_airport_zone, classify_zone_priority
)
from app.models.lpi_certificate import LPICertificateRecord
from datetime import datetime

router = APIRouter()


class LPIIssueRequest(BaseModel):
    latitude: float
    longitude: float
    property_address: str
    owner_name: str
    property_area_sqm: float
    state: str = "Delhi"
    city: str = "Delhi"
    locality: str = ""
    lead_id: Optional[int] = None
    issued_by_agent_id: Optional[int] = None


class LPIZoneCheckRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0


@router.get("/lpi/verify/{lpi_code}")
def verify_lpi(lpi_code: str):
    """Public-facing LPI verification endpoint."""
    return verify_lpi_code(lpi_code)


@router.post("/lpi/zone-check")
def check_airport_zone(req: LPIZoneCheckRequest):
    """Check if coordinates fall within any airport acquisition zone."""
    zones = find_airport_zones(req.latitude, req.longitude, req.radius_km)
    in_zone, nearest = is_in_airport_zone(req.latitude, req.longitude, req.radius_km)
    priority = classify_zone_priority(nearest)

    return {
        "latitude": req.latitude,
        "longitude": req.longitude,
        "in_airport_zone": in_zone,
        "zone_priority": priority,
        "requires_lpi": in_zone,
        "airports_within_radius": [
            {
                "iata_code": z.airport.iata_code,
                "airport_name": z.airport.airport_name,
                "city": z.airport.city,
                "distance_km": z.distance_km,
                "zone_label": z.zone_label,
                "airport_tier": z.airport.tier,
            }
            for z in zones
        ],
    }


@router.post("/lpi/issue", status_code=201)
def issue_lpi_certificate(req: LPIIssueRequest, db: Session = Depends(get_db)):
    """Issue a new LPI certificate for a property."""
    cert = issue_certificate(
        latitude=req.latitude,
        longitude=req.longitude,
        property_area_sqm=req.property_area_sqm,
        property_address=req.property_address,
        owner_name=req.owner_name,
        state=req.state,
        city=req.city,
        locality=req.locality,
    )

    first_parcel = cert.parcels[0] if cert.parcels else None

    # Persist to DB
    record = LPICertificateRecord(
        certificate_id=cert.certificate_id,
        lpi_codes=cert.lpi_codes,
        property_address=cert.property_address,
        owner_name=cert.owner_name,
        city=req.city,
        state=req.state,
        latitude=req.latitude,
        longitude=req.longitude,
        total_area_sqm=cert.total_area_sqm,
        in_airport_zone=first_parcel.in_airport_zone if first_parcel else False,
        nearest_airport_iata=first_parcel.nearest_airport_iata if first_parcel else None,
        airport_distance_km=first_parcel.airport_distance_km if first_parcel else None,
        zone_priority=classify_zone_priority(
            type("ZM", (), {"airport": type("A", (), {"tier": "metro"})(), "distance_km": first_parcel.airport_distance_km or 99})()
            if first_parcel and first_parcel.in_airport_zone else None
        ),
        status=cert.status,
        issued_at=cert.issued_at,
        valid_until=cert.valid_until,
        flags=cert.flags,
        satellite_id=cert.satellite_id,
        scan_resolution_cm=cert.scan_resolution_cm,
        lidar_scan_date=first_parcel.lidar_scan_date if first_parcel else None,
        seismic_zone=first_parcel.seismic_zone if first_parcel else None,
        lead_id=req.lead_id,
        issued_by_agent_id=req.issued_by_agent_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "certificate_id": cert.certificate_id,
        "lpi_codes": cert.lpi_codes[:3],        # First 3 parcel codes
        "total_parcels": len(cert.parcels),
        "property_address": cert.property_address,
        "owner_name": cert.owner_name,
        "issued_at": cert.issued_at.isoformat(),
        "valid_until": cert.valid_until.isoformat(),
        "in_airport_zone": first_parcel.in_airport_zone if first_parcel else False,
        "flags": cert.flags,
        "issued_by": cert.issued_by,
        "legal_reference": cert.legal_reference,
        "status": "issued",
    }


@router.get("/lpi/certificates")
def list_certificates(
    city: Optional[str] = None,
    in_airport_zone: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(LPICertificateRecord)
    if city:
        query = query.filter(LPICertificateRecord.city == city)
    if in_airport_zone is not None:
        query = query.filter(LPICertificateRecord.in_airport_zone == in_airport_zone)
    certs = query.order_by(LPICertificateRecord.issued_at.desc()).limit(100).all()
    return [
        {
            "id": c.id,
            "certificate_id": c.certificate_id,
            "property_address": c.property_address,
            "owner_name": c.owner_name,
            "city": c.city,
            "in_airport_zone": c.in_airport_zone,
            "nearest_airport_iata": c.nearest_airport_iata,
            "airport_distance_km": c.airport_distance_km,
            "status": c.status,
            "issued_at": c.issued_at.isoformat() if c.issued_at else None,
        }
        for c in certs
    ]


@router.get("/lpi/stats")
def lpi_stats(db: Session = Depends(get_db)):
    """Dashboard stats for LPI issuance."""
    from sqlalchemy import func
    total = db.query(func.count(LPICertificateRecord.id)).scalar()
    in_zone = db.query(func.count(LPICertificateRecord.id)).filter(
        LPICertificateRecord.in_airport_zone == True
    ).scalar()
    by_city = db.query(
        LPICertificateRecord.city,
        func.count(LPICertificateRecord.id)
    ).group_by(LPICertificateRecord.city).all()

    return {
        "total_certificates_issued": total,
        "airport_zone_certificates": in_zone,
        "revenue_potential_inr": total * 15000,
        "by_city": [{"city": city, "count": count} for city, count in by_city],
    }
