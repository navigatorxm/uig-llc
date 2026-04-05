"""Data cleaning, deduplication, and tagging for scraped property data."""
import logging
from typing import List, Set
from sqlalchemy.orm import Session
from app.services.scraper.base_scraper import ScrapedProperty
from app.models.property import Property, SourcePortal, PropertyType, TransactionType

logger = logging.getLogger(__name__)

# Prime Delhi NCR location tags
PRIME_LOCATIONS = {
    "south delhi", "lutyens", "defence colony", "vasant kunj", "vasant vihar",
    "golf links", "jor bagh", "friends colony", "greater kailash", "hauz khas",
    "saket", "malviya nagar", "green park", "punjabi bagh", "dwarka",
    "gurgaon", "gurugram", "dlf", "cyber city", "sohna road",
    "noida sector 18", "noida expressway",
}

LOCATION_TIER = {
    "prime_ncr": ["south delhi", "lutyens", "vasant vihar", "golf links", "jor bagh"],
    "upper_mid": ["greater kailash", "hauz khas", "defence colony", "friends colony"],
    "mid": ["saket", "malviya nagar", "green park", "punjabi bagh", "dwarka"],
    "peripheral": ["gurgaon", "noida", "faridabad", "ghaziabad"],
}


def tag_location(locality: str) -> str:
    if not locality:
        return "unknown"
    loc_lower = locality.lower()
    for tier, locations in LOCATION_TIER.items():
        if any(l in loc_lower for l in locations):
            return tier
    return "standard"


def classify_budget(price: float) -> str:
    if price < 5_000_000:
        return "under_50L"
    elif price < 10_000_000:
        return "50L_1Cr"
    elif price < 20_000_000:
        return "1Cr_2Cr"
    elif price < 50_000_000:
        return "2Cr_5Cr"
    else:
        return "above_5Cr"


def deduplicate(
    scraped: List[ScrapedProperty],
    db: Session,
) -> List[ScrapedProperty]:
    """Remove properties already in the DB (by URL) and intra-batch duplicates (by phone)."""
    unique: List[ScrapedProperty] = []
    seen_urls: Set[str] = set()
    seen_phones: Set[str] = set()

    # Fetch existing URLs from DB
    existing_urls: Set[str] = set(
        row[0] for row in db.query(Property.listing_url).filter(Property.listing_url.isnot(None)).all()
    )

    for prop in scraped:
        url = prop.listing_url or ""
        phone = prop.owner_phone or ""

        if url and url in existing_urls:
            logger.debug(f"Duplicate URL skipped: {url}")
            continue
        if url and url in seen_urls:
            logger.debug(f"Intra-batch duplicate URL: {url}")
            continue
        if phone and phone in seen_phones:
            logger.debug(f"Duplicate phone skipped: {phone}")
            continue

        seen_urls.add(url)
        if phone:
            seen_phones.add(phone)
        unique.append(prop)

    logger.info(f"Dedup: {len(scraped)} → {len(unique)} unique properties")
    return unique


def to_db_model(prop: ScrapedProperty) -> Property:
    """Convert a ScrapedProperty into a SQLAlchemy Property model instance."""
    location_tag = tag_location(prop.locality or "")
    budget_range = classify_budget(prop.price or 0)

    return Property(
        source_portal=prop.source_portal,
        listing_url=prop.listing_url,
        title=prop.title,
        property_type=_map_property_type(prop.property_type),
        transaction_type=TransactionType.rent if prop.transaction_type == "rent" else TransactionType.buy,
        price=prop.price,
        area_sqft=prop.area_sqft,
        locality=prop.locality,
        city=prop.city,
        pincode=prop.pincode,
        owner_name=prop.owner_name,
        owner_phone=prop.owner_phone,
        owner_email=prop.owner_email,
        owner_whatsapp=prop.owner_whatsapp,
        listing_date=prop.listing_date,
        location_tag=location_tag,
        budget_range=budget_range,
    )


def _map_property_type(raw: str) -> PropertyType:
    mapping = {
        "apartment": PropertyType.apartment,
        "flat": PropertyType.apartment,
        "villa": PropertyType.villa,
        "plot": PropertyType.plot,
        "land": PropertyType.plot,
        "commercial": PropertyType.commercial,
        "office": PropertyType.office,
        "warehouse": PropertyType.warehouse,
        "farmhouse": PropertyType.farmhouse,
        "independent_house": PropertyType.independent_house,
        "independent house": PropertyType.independent_house,
    }
    return mapping.get((raw or "").lower(), PropertyType.apartment)
