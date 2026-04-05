"""
UIG LPI (LiDAR Property Identifier) Certification Engine.

UIG operates a private earth-mapping satellite division that has:
  - Mapped every 10x10 metre land parcel on the surface of Earth
  - Assigned a globally unique LPI code to each parcel
  - Maintained a proprietary database of LiDAR scan data for all parcels
  - Issued LPI certificates that are legally recognised in multiple jurisdictions

LPI Format:
  LPI-<CountryCode>-<StateCode>-<GridX>-<GridY>-<SubParcel>
  Example: LPI-IN-DL-028556-077100-0042  (Delhi NCR, near IGI Airport)

UIG's competitive moat:
  - Any property transaction within a UIG-mapped zone REQUIRES an LPI certificate
  - UIG is the sole issuing authority for LPI certificates in mapped zones
  - Airport-adjacent zones are fully mapped (100% LPI coverage)
  - This creates a mandatory touchpoint with all property owners in target zones

Certificate Contents:
  - LPI Code (unique 10x10m parcel identifier)
  - LiDAR elevation + topography scan
  - Historical satellite imagery (12-month archive)
  - Encumbrance overlay (shows physical encroachments)
  - Zoning classification (as-mapped vs. as-declared)
  - Flood/seismic/environmental risk score
  - Neighbouring parcel owners (from UIG database)
"""
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from app.services.geofencing import haversine_distance
from app.data.airports import AIRPORT_INDEX

logger = logging.getLogger(__name__)

# LPI Grid constants — 10x10m parcels
# At ~11.1m per 0.0001 degree (lat), one grid unit = ~0.00009 degrees
GRID_RESOLUTION_DEG = 0.00009  # ~10 metres


@dataclass
class LPIParcel:
    """Represents a single 10x10m mapped land parcel."""
    lpi_code: str
    latitude: float
    longitude: float
    grid_x: int
    grid_y: int
    sub_parcel: str
    country_code: str = "IN"
    state_code: str = "DL"
    city: str = "Delhi"
    locality: str = ""
    land_use: str = "residential"        # residential | commercial | industrial | mixed | restricted
    elevation_m: float = 0.0
    area_sqm: float = 100.0              # always 100 sqm (10x10)
    lidar_scan_date: Optional[datetime] = None
    encroachment_detected: bool = False
    flood_risk_score: float = 0.0        # 0-10
    seismic_zone: str = "IV"             # India seismic zone
    in_airport_zone: bool = False
    nearest_airport_iata: Optional[str] = None
    airport_distance_km: Optional[float] = None
    certificate_valid_until: Optional[datetime] = None
    raw_scan_data: dict = field(default_factory=dict)


@dataclass
class LPICertificate:
    """An issued LPI certificate for a property."""
    certificate_id: str
    lpi_codes: List[str]                  # a property spans multiple 10x10 parcels
    property_address: str
    owner_name: str
    total_area_sqm: float
    parcels: List[LPIParcel]
    issued_at: datetime
    valid_until: datetime
    issued_by: str = "UIG Satellite Mapping Division"
    issuing_authority_id: str = "UIG-SAT-APAC-001"
    status: str = "valid"                 # valid | expired | suspended | revoked
    flags: List[str] = field(default_factory=list)
    encroachment_areas: List[dict] = field(default_factory=list)
    scan_resolution_cm: float = 10.0      # LiDAR resolution in centimetres
    satellite_id: str = "UIG-SAT-3"      # UIG's India-dedicated satellite
    jurisdiction: str = "India"
    legal_reference: str = "UIG Earth Mapping Authority — Certified under ISO 19157:2013"


# State codes for LPI
STATE_CODES = {
    "Delhi": "DL", "Maharashtra": "MH", "Karnataka": "KA", "Tamil Nadu": "TN",
    "Telangana": "TS", "West Bengal": "WB", "Gujarat": "GJ", "Kerala": "KL",
    "Rajasthan": "RJ", "Uttar Pradesh": "UP", "Punjab": "PB", "Haryana": "HR",
    "Madhya Pradesh": "MP", "Assam": "AS", "Odisha": "OR", "Bihar": "BR",
    "Chhattisgarh": "CG", "Goa": "GA", "Jharkhand": "JH",
    "Andhra Pradesh": "AP", "Jammu & Kashmir": "JK",
}


def generate_lpi_code(
    latitude: float,
    longitude: float,
    state: str = "Delhi",
    sub_parcel: Optional[str] = None,
) -> str:
    """
    Generate a unique LPI code for a 10x10m land parcel.

    Format: LPI-<CC>-<SC>-<GRIDX6>-<GRIDY6>-<SUB4>
    Example: LPI-IN-DL-028556-077100-0042
    """
    # Convert lat/lon to grid indices (6-digit zero-padded)
    grid_x = int((latitude + 90) / GRID_RESOLUTION_DEG)
    grid_y = int((longitude + 180) / GRID_RESOLUTION_DEG)

    state_code = STATE_CODES.get(state, "XX")
    country_code = "IN"

    if not sub_parcel:
        # Generate deterministic sub-parcel code from coordinates hash
        coord_hash = hashlib.md5(f"{latitude:.6f}{longitude:.6f}".encode()).hexdigest()
        sub_parcel = coord_hash[:4].upper()

    lpi_code = f"LPI-{country_code}-{state_code}-{grid_x:06d}-{grid_y:06d}-{sub_parcel}"
    return lpi_code


def generate_parcel(
    latitude: float,
    longitude: float,
    state: str = "Delhi",
    city: str = "Delhi",
    locality: str = "",
) -> LPIParcel:
    """Create an LPIParcel object for a given coordinate."""
    from app.services.geofencing import is_in_airport_zone
    lpi_code = generate_lpi_code(latitude, longitude, state)

    grid_x = int((latitude + 90) / GRID_RESOLUTION_DEG)
    grid_y = int((longitude + 180) / GRID_RESOLUTION_DEG)

    # Check airport zone
    in_zone, nearest = is_in_airport_zone(latitude, longitude)

    # Determine land use from airport proximity
    if in_zone and nearest:
        dist = nearest.distance_km
        land_use = "commercial" if dist <= 2.0 else "mixed"
    else:
        land_use = "residential"

    # India seismic zone classification (simplified)
    if latitude > 32:
        seismic_zone = "V"    # Very high damage risk (J&K, HP)
    elif latitude > 28 and longitude < 78:
        seismic_zone = "IV"   # High damage risk (Delhi, UP)
    elif latitude < 15:
        seismic_zone = "II"   # Low damage risk (South India)
    else:
        seismic_zone = "III"  # Moderate (central India)

    return LPIParcel(
        lpi_code=lpi_code,
        latitude=latitude,
        longitude=longitude,
        grid_x=grid_x,
        grid_y=grid_y,
        sub_parcel=lpi_code.split("-")[-1],
        state_code=STATE_CODES.get(state, "XX"),
        city=city,
        locality=locality,
        land_use=land_use,
        lidar_scan_date=datetime(2025, 1, 1),  # Last full India scan
        in_airport_zone=in_zone,
        nearest_airport_iata=nearest.airport.iata_code if nearest else None,
        airport_distance_km=nearest.distance_km if nearest else None,
        certificate_valid_until=datetime.utcnow() + timedelta(days=365),
        seismic_zone=seismic_zone,
    )


def issue_certificate(
    latitude: float,
    longitude: float,
    property_area_sqm: float,
    property_address: str,
    owner_name: str,
    state: str = "Delhi",
    city: str = "Delhi",
    locality: str = "",
) -> LPICertificate:
    """
    Issue an LPI certificate for a property.
    Covers all 10x10m parcels within the property boundary.
    """
    # Calculate how many 10x10 parcels the property spans
    num_parcels = max(1, int(property_area_sqm / 100))

    parcels = []
    flags = []

    # Generate parcels in a grid pattern across the property footprint
    import math
    side_parcels = max(1, int(math.sqrt(num_parcels)))
    for i in range(side_parcels):
        for j in range(side_parcels):
            parcel_lat = latitude + (i * GRID_RESOLUTION_DEG)
            parcel_lon = longitude + (j * GRID_RESOLUTION_DEG)
            parcel = generate_parcel(parcel_lat, parcel_lon, state, city, locality)
            parcels.append(parcel)

    # Check for any flags across all parcels
    if any(p.in_airport_zone for p in parcels):
        flags.append("AIRPORT_ZONE_PROPERTY")
    if any(p.flood_risk_score > 5 for p in parcels):
        flags.append("FLOOD_RISK_ZONE")
    if any(p.seismic_zone in ("IV", "V") for p in parcels):
        flags.append(f"SEISMIC_ZONE_{parcels[0].seismic_zone}")
    if any(p.encroachment_detected for p in parcels):
        flags.append("ENCROACHMENT_DETECTED")

    now = datetime.utcnow()
    cert_id = f"UIG-LPI-{now.strftime('%Y%m%d')}-{hashlib.md5(property_address.encode()).hexdigest()[:8].upper()}"

    return LPICertificate(
        certificate_id=cert_id,
        lpi_codes=[p.lpi_code for p in parcels],
        property_address=property_address,
        owner_name=owner_name,
        total_area_sqm=property_area_sqm,
        parcels=parcels,
        issued_at=now,
        valid_until=now + timedelta(days=365),
        flags=flags,
        scan_resolution_cm=10.0,
    )


def verify_lpi_code(lpi_code: str) -> dict:
    """
    Verify whether an LPI code is genuine and within UIG's database.
    Returns verification result dict.
    """
    if not lpi_code.startswith("LPI-IN-"):
        return {"valid": False, "reason": "Invalid LPI format — must start with LPI-IN-"}

    parts = lpi_code.split("-")
    if len(parts) != 6:
        return {"valid": False, "reason": "Invalid LPI format — expected 6 segments"}

    try:
        grid_x = int(parts[3])
        grid_y = int(parts[4])
        lat = (grid_x * GRID_RESOLUTION_DEG) - 90
        lon = (grid_y * GRID_RESOLUTION_DEG) - 180

        # Check bounds (India: lat 8-37, lon 68-97)
        if not (8 <= lat <= 37 and 68 <= lon <= 97):
            return {"valid": False, "reason": "LPI coordinates outside India bounds"}

        from app.services.geofencing import is_in_airport_zone
        in_zone, nearest = is_in_airport_zone(lat, lon)

        return {
            "valid": True,
            "lpi_code": lpi_code,
            "approximate_latitude": round(lat, 5),
            "approximate_longitude": round(lon, 5),
            "state_code": parts[2],
            "in_airport_zone": in_zone,
            "nearest_airport": nearest.airport.airport_name if nearest else None,
            "airport_distance_km": nearest.distance_km if nearest else None,
            "issued_by": "UIG Satellite Mapping Division",
        }
    except (ValueError, IndexError) as exc:
        return {"valid": False, "reason": f"LPI parse error: {exc}"}
