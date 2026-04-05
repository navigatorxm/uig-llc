"""
Geofencing service — determines if a property falls within a UIG acquisition zone.

Primary zones: 5km radius from all major Indian airports.
All airport-zone properties are automatically flagged as HIGH PRIORITY and
require LPI (LiDAR Property Identifier) certification from UIG's satellite division.
"""
import math
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
from app.data.airports import AIRPORTS, AIRPORT_INDEX, AirportZone

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0


@dataclass
class ZoneMatch:
    airport: AirportZone
    distance_km: float
    within_zone: bool
    zone_label: str          # e.g. "DEL-5km", "BOM-3.2km"
    requires_lpi: bool = True


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km between two lat/lon points."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def find_airport_zones(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
) -> List[ZoneMatch]:
    """
    Find all airport zones a property falls within.
    Returns a list of ZoneMatch objects sorted by distance (nearest first).
    """
    matches = []
    for airport in AIRPORTS:
        dist = haversine_distance(latitude, longitude, airport.latitude, airport.longitude)
        if dist <= radius_km:
            matches.append(ZoneMatch(
                airport=airport,
                distance_km=round(dist, 2),
                within_zone=True,
                zone_label=f"{airport.iata_code}-{dist:.1f}km",
                requires_lpi=True,
            ))

    return sorted(matches, key=lambda x: x.distance_km)


def is_in_airport_zone(
    latitude: Optional[float],
    longitude: Optional[float],
    radius_km: float = 5.0,
) -> Tuple[bool, Optional[ZoneMatch]]:
    """
    Quick check: is a property within ANY airport zone?
    Returns (True, nearest_match) or (False, None).
    """
    if latitude is None or longitude is None:
        return False, None

    zones = find_airport_zones(latitude, longitude, radius_km)
    if zones:
        return True, zones[0]
    return False, None


def classify_zone_priority(zone_match: Optional[ZoneMatch]) -> str:
    """
    Classify acquisition priority based on airport zone proximity.
    Returns: "critical" | "high" | "elevated" | "standard"
    """
    if not zone_match:
        return "standard"
    dist = zone_match.distance_km
    tier = zone_match.airport.tier
    if dist <= 1.0:
        return "critical"      # Directly adjacent to airport boundary
    elif dist <= 2.5 and tier == "metro":
        return "critical"
    elif dist <= 2.5:
        return "high"
    elif dist <= 4.0 and tier == "metro":
        return "high"
    elif dist <= 5.0:
        return "elevated"
    return "standard"


def get_zone_label_for_city(city: str) -> List[str]:
    """Return all airport zone labels for a given city."""
    from app.data.airports import CITY_AIRPORTS
    iata_codes = CITY_AIRPORTS.get(city, [])
    return [f"{code}-5km" for code in iata_codes]


def enrich_property_with_zone_data(property_data: dict) -> dict:
    """
    Enrich a property dict with zone classification and LPI requirement flags.
    Modifies in place and returns updated dict.
    """
    lat = property_data.get("latitude")
    lon = property_data.get("longitude")

    in_zone, nearest = is_in_airport_zone(lat, lon)
    property_data["in_airport_zone"] = in_zone
    property_data["requires_lpi"] = in_zone
    property_data["zone_priority"] = classify_zone_priority(nearest)

    if nearest:
        property_data["nearest_airport_iata"] = nearest.airport.iata_code
        property_data["nearest_airport_name"] = nearest.airport.airport_name
        property_data["airport_distance_km"] = nearest.distance_km
        property_data["zone_label"] = nearest.zone_label
    else:
        property_data["nearest_airport_iata"] = None
        property_data["nearest_airport_name"] = None
        property_data["airport_distance_km"] = None
        property_data["zone_label"] = None

    return property_data
