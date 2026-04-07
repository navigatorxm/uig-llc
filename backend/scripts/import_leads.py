#!/usr/bin/env python3
"""
UIG Lead Import Script
======================
Universal importer for existing leads from CSV, Excel (.xlsx), or JSON.

Supports messy column names from WhatsApp exports, MagicBricks/99acres
manual exports, and hand-typed spreadsheets.

Usage:
    python scripts/import_leads.py --file leads.csv
    python scripts/import_leads.py --file leads.xlsx --city Mumbai
    python scripts/import_leads.py --file leads.json --dry-run
    python scripts/import_leads.py --file leads.csv --score --city "Delhi NCR"

Options:
    --file      Path to CSV, XLSX, or JSON file
    --city      Default city if not in file (default: Delhi NCR)
    --state     Default state if not in file (default: Delhi)
    --dry-run   Parse and show what would be imported, no DB writes
    --score     AI-score each lead after import (requires ANTHROPIC_API_KEY)
    --batch     Batch size for DB inserts (default: 50)
"""

import argparse
import json
import logging
import os
import sys
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# ── project root on sys.path ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("import_leads")


# ── column name aliases ───────────────────────────────────────────────────────
# Maps every reasonable column name variant → canonical field name
COLUMN_ALIASES: Dict[str, str] = {
    # owner name
    "name": "owner_name",
    "owner": "owner_name",
    "owner name": "owner_name",
    "owner_name": "owner_name",
    "contact name": "owner_name",
    "contact_name": "owner_name",
    "seller name": "owner_name",
    "seller": "owner_name",
    "landlord": "owner_name",
    "landlord name": "owner_name",
    "full name": "owner_name",
    "fullname": "owner_name",
    # phone
    "phone": "phone",
    "phone number": "phone",
    "phone_number": "phone",
    "mobile": "phone",
    "mobile number": "phone",
    "mobile_number": "phone",
    "contact": "phone",
    "contact number": "phone",
    "cell": "phone",
    "whatsapp": "whatsapp",
    "whatsapp number": "whatsapp",
    "whatsapp_number": "whatsapp",
    "wa number": "whatsapp",
    # email
    "email": "email",
    "email address": "email",
    "email_address": "email",
    "e-mail": "email",
    # address / location
    "address": "property_address",
    "property address": "property_address",
    "property_address": "property_address",
    "location": "locality",
    "locality": "locality",
    "area": "locality",
    "sector": "locality",
    "neighbourhood": "locality",
    "neighborhood": "locality",
    "city": "city",
    "state": "state",
    "pincode": "pincode",
    "pin code": "pincode",
    "pin": "pincode",
    "zip": "pincode",
    # property details
    "property type": "property_type",
    "property_type": "property_type",
    "type": "property_type",
    "transaction": "transaction_type",
    "transaction type": "transaction_type",
    "transaction_type": "transaction_type",
    "listing type": "transaction_type",
    "deal type": "transaction_type",
    "buy or rent": "transaction_type",
    "price": "price",
    "asking price": "price",
    "expected price": "price",
    "budget": "price",
    "cost": "price",
    "rate": "price",
    "area sqft": "area_sqft",
    "area_sqft": "area_sqft",
    "size": "area_sqft",
    "area (sqft)": "area_sqft",
    "sqft": "area_sqft",
    "sq ft": "area_sqft",
    "carpet area": "area_sqft",
    "built up area": "area_sqft",
    # source
    "source": "source_portal",
    "portal": "source_portal",
    "source portal": "source_portal",
    "platform": "source_portal",
    "website": "source_portal",
    "from": "source_portal",
    # notes
    "notes": "notes",
    "note": "notes",
    "remarks": "notes",
    "comments": "notes",
    "description": "notes",
    "details": "notes",
    # url
    "url": "listing_url",
    "link": "listing_url",
    "listing url": "listing_url",
    "listing_url": "listing_url",
    "listing link": "listing_url",
    "property url": "listing_url",
}

PROPERTY_TYPE_MAP = {
    "flat": "apartment",
    "apartment": "apartment",
    "2bhk": "apartment",
    "3bhk": "apartment",
    "house": "independent_house",
    "villa": "villa",
    "plot": "plot",
    "land": "plot",
    "commercial": "commercial",
    "office": "commercial",
    "shop": "commercial",
    "industrial": "industrial",
    "warehouse": "industrial",
    "farm": "farmhouse",
    "farmhouse": "farmhouse",
}

TRANSACTION_TYPE_MAP = {
    "buy": "buy",
    "purchase": "buy",
    "sale": "buy",
    "sell": "buy",
    "selling": "buy",
    "for sale": "buy",
    "rent": "rent",
    "rental": "rent",
    "lease": "rent",
    "renting": "rent",
    "for rent": "rent",
}


@dataclass
class ImportedLead:
    owner_name: str = ""
    phone: str = ""
    email: str = ""
    whatsapp: str = ""
    property_address: str = ""
    locality: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""
    property_type: str = "apartment"
    transaction_type: str = "buy"
    price: Optional[float] = None
    area_sqft: Optional[float] = None
    source_portal: str = "manual"
    listing_url: str = ""
    notes: str = ""
    raw_row: dict = field(default_factory=dict)
    row_number: int = 0
    warnings: List[str] = field(default_factory=list)


# ── normalisation helpers ─────────────────────────────────────────────────────

def _clean_phone(raw: str) -> str:
    """Strip to digits, ensure India prefix."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", str(raw))
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    return digits if len(digits) == 10 else digits


def _clean_price(raw: Any) -> Optional[float]:
    if raw is None or str(raw).strip() in ("", "-", "NA", "N/A", "na"):
        return None
    raw_str = str(raw).lower().replace(",", "").replace("₹", "").replace("rs", "").strip()
    multiplier = 1.0
    if "cr" in raw_str or "crore" in raw_str:
        multiplier = 1e7
        raw_str = re.sub(r"(crore|cr)", "", raw_str).strip()
    elif "lakh" in raw_str or "lac" in raw_str or "l" in raw_str:
        multiplier = 1e5
        raw_str = re.sub(r"(lakh|lac|l\b)", "", raw_str).strip()
    try:
        return float(raw_str) * multiplier
    except ValueError:
        return None


def _clean_area(raw: Any) -> Optional[float]:
    if raw is None or str(raw).strip() in ("", "-", "NA"):
        return None
    try:
        return float(re.sub(r"[^\d.]", "", str(raw)))
    except ValueError:
        return None


def _normalise_header(col: str) -> str:
    return COLUMN_ALIASES.get(col.lower().strip(), col.lower().strip())


def _map_columns(headers: List[str]) -> Dict[str, str]:
    """Return {canonical_field: source_column} mapping."""
    mapping: Dict[str, str] = {}
    for col in headers:
        canonical = _normalise_header(col)
        if canonical not in mapping:
            mapping[canonical] = col
    return mapping


# ── file readers ──────────────────────────────────────────────────────────────

def read_csv(path: Path) -> List[Dict[str, Any]]:
    import csv
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def read_excel(path: Path) -> List[Dict[str, Any]]:
    try:
        import openpyxl
    except ImportError:
        log.error("openpyxl not installed. Run: pip install openpyxl")
        sys.exit(1)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
    return [dict(zip(headers, row)) for row in rows[1:]]


def read_json(path: Path) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # support {"leads": [...]} or {"data": [...]}
        for key in ("leads", "data", "records", "results"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return []


def load_file(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return read_excel(path)
    elif suffix == ".json":
        return read_json(path)
    else:
        log.error(f"Unsupported file type: {suffix}. Use CSV, XLSX, or JSON.")
        sys.exit(1)


# ── row → ImportedLead ────────────────────────────────────────────────────────

def parse_row(
    row: Dict[str, Any],
    mapping: Dict[str, str],
    row_num: int,
    defaults: Dict[str, str],
) -> ImportedLead:
    lead = ImportedLead(raw_row=row, row_number=row_num)

    def get(field_name: str, fallback: str = "") -> str:
        col = mapping.get(field_name)
        if col and col in row and row[col] is not None:
            return str(row[col]).strip()
        return fallback

    lead.owner_name = get("owner_name")
    lead.phone = _clean_phone(get("phone"))
    lead.whatsapp = _clean_phone(get("whatsapp")) or lead.phone
    lead.email = get("email").lower()
    lead.property_address = get("property_address")
    lead.locality = get("locality")
    lead.city = get("city") or defaults.get("city", "Delhi NCR")
    lead.state = get("state") or defaults.get("state", "Delhi")
    lead.pincode = get("pincode")
    lead.listing_url = get("listing_url")
    lead.notes = get("notes")
    lead.source_portal = get("source_portal") or "manual"

    # property type
    raw_type = get("property_type", "apartment").lower()
    for key, val in PROPERTY_TYPE_MAP.items():
        if key in raw_type:
            lead.property_type = val
            break
    else:
        lead.property_type = "apartment"

    # transaction type
    raw_tx = get("transaction_type", "buy").lower()
    for key, val in TRANSACTION_TYPE_MAP.items():
        if key in raw_tx:
            lead.transaction_type = val
            break
    else:
        lead.transaction_type = "buy"

    lead.price = _clean_price(row.get(mapping.get("price", ""), None))
    lead.area_sqft = _clean_area(row.get(mapping.get("area_sqft", ""), None))

    # Warnings
    if not lead.owner_name:
        lead.warnings.append("missing owner_name")
    if not lead.phone and not lead.email:
        lead.warnings.append("no contact info (phone or email)")
    if not lead.property_address and not lead.locality:
        lead.warnings.append("no location info")

    return lead


def parse_all_rows(
    rows: List[Dict[str, Any]],
    defaults: Dict[str, str],
) -> List[ImportedLead]:
    if not rows:
        return []
    headers = list(rows[0].keys())
    mapping = _map_columns(headers)
    log.info(f"Detected column mapping: {mapping}")
    leads = []
    for i, row in enumerate(rows, start=2):
        # skip completely empty rows
        if all(v is None or str(v).strip() == "" for v in row.values()):
            continue
        lead = parse_row(row, mapping, row_num=i, defaults=defaults)
        leads.append(lead)
    return leads


# ── DB insert ─────────────────────────────────────────────────────────────────

def insert_leads(leads: List[ImportedLead], batch_size: int = 50) -> Dict[str, int]:
    from app.database import SessionLocal
    from app.models.lead import Lead, PipelineStage
    from app.models.property import Property, PropertyType, TransactionType, SourcePortal

    session = SessionLocal()
    stats = {"inserted": 0, "skipped_duplicate": 0, "skipped_no_contact": 0, "errors": 0}

    try:
        for i in range(0, len(leads), batch_size):
            batch = leads[i: i + batch_size]
            for lead in batch:
                if not lead.phone and not lead.email:
                    stats["skipped_no_contact"] += 1
                    continue

                # dedup by phone or email
                existing = None
                if lead.phone:
                    existing = session.query(Lead).filter(Lead.phone == lead.phone).first()
                if not existing and lead.email:
                    existing = session.query(Lead).filter(Lead.email == lead.email).first()
                if existing:
                    stats["skipped_duplicate"] += 1
                    log.debug(f"Row {lead.row_number}: duplicate (phone={lead.phone})")
                    continue

                try:
                    db_lead = Lead(
                        owner_name=lead.owner_name or "Unknown",
                        phone=lead.phone,
                        email=lead.email or None,
                        whatsapp=lead.whatsapp or None,
                        pipeline_stage=PipelineStage.new_lead,
                        notes=lead.notes,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(db_lead)
                    session.flush()  # get db_lead.id

                    # attach a property record
                    prop_type_str = lead.property_type
                    try:
                        prop_type = PropertyType(prop_type_str)
                    except ValueError:
                        prop_type = PropertyType.apartment

                    tx_type_str = lead.transaction_type
                    try:
                        tx_type = TransactionType(tx_type_str)
                    except ValueError:
                        tx_type = TransactionType.buy

                    try:
                        source = SourcePortal(lead.source_portal)
                    except ValueError:
                        source = SourcePortal.other

                    db_property = Property(
                        lead_id=db_lead.id,
                        source_portal=source,
                        listing_url=lead.listing_url or "",
                        title=lead.property_address or f"{lead.locality}, {lead.city}",
                        property_type=prop_type,
                        transaction_type=tx_type,
                        price=lead.price,
                        area_sqft=lead.area_sqft,
                        location=lead.property_address or lead.locality,
                        locality=lead.locality,
                        city=lead.city,
                        pincode=lead.pincode or None,
                        owner_name=lead.owner_name or "Unknown",
                        owner_phone=lead.phone,
                        owner_email=lead.email or None,
                        owner_whatsapp=lead.whatsapp or None,
                        scraped_at=datetime.utcnow(),
                    )
                    session.add(db_property)
                    stats["inserted"] += 1

                except Exception as exc:
                    log.error(f"Row {lead.row_number} insert error: {exc}")
                    stats["errors"] += 1
                    session.rollback()
                    continue

            session.commit()
            log.info(
                f"Batch {i // batch_size + 1}: "
                f"{stats['inserted']} inserted so far"
            )

    except Exception as exc:
        session.rollback()
        log.error(f"Fatal DB error: {exc}")
        raise
    finally:
        session.close()

    return stats


# ── AI scoring pass ───────────────────────────────────────────────────────────

def score_imported_leads():
    """Trigger Claude lead scoring for all new_lead stage records."""
    try:
        from app.database import SessionLocal
        from app.models.lead import Lead, PipelineStage
        from app.services.ai.lead_scorer import LeadScorer

        session = SessionLocal()
        scorer = LeadScorer()
        leads = session.query(Lead).filter(
            Lead.pipeline_stage == PipelineStage.new_lead,
            Lead.lead_score.is_(None),
        ).all()

        log.info(f"Scoring {len(leads)} unscored leads with Claude AI...")
        scored = 0
        for lead in leads:
            try:
                result = scorer.score_lead(lead)
                lead.lead_score = result.score
                lead.notes = (lead.notes or "") + f"\n[AI Score: {result.score}/100] {result.reasoning}"
                scored += 1
            except Exception as exc:
                log.warning(f"Scoring failed for lead {lead.id}: {exc}")

        session.commit()
        log.info(f"Scored {scored}/{len(leads)} leads.")
        session.close()
    except Exception as exc:
        log.error(f"Scoring pass failed: {exc}")


# ── reporting ─────────────────────────────────────────────────────────────────

def print_summary(leads: List[ImportedLead], stats: Optional[Dict] = None):
    total = len(leads)
    with_phone = sum(1 for l in leads if l.phone)
    with_email = sum(1 for l in leads if l.email)
    with_whatsapp = sum(1 for l in leads if l.whatsapp)
    with_warnings = sum(1 for l in leads if l.warnings)
    buy_leads = sum(1 for l in leads if l.transaction_type == "buy")
    rent_leads = sum(1 for l in leads if l.transaction_type == "rent")

    print("\n" + "=" * 60)
    print("  UIG LEAD IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Total rows parsed      : {total}")
    print(f"  With phone number      : {with_phone}")
    print(f"  With email             : {with_email}")
    print(f"  With WhatsApp          : {with_whatsapp}")
    print(f"  Buy leads              : {buy_leads}")
    print(f"  Rent leads             : {rent_leads}")
    print(f"  Rows with warnings     : {with_warnings}")

    if stats:
        print("-" * 60)
        print(f"  DB Inserted            : {stats['inserted']}")
        print(f"  Skipped (duplicate)    : {stats['skipped_duplicate']}")
        print(f"  Skipped (no contact)   : {stats['skipped_no_contact']}")
        print(f"  Errors                 : {stats['errors']}")

    if with_warnings:
        print("\n  Rows with warnings:")
        for lead in leads:
            if lead.warnings:
                print(f"    Row {lead.row_number:>4}: {', '.join(lead.warnings)}")

    # City breakdown
    from collections import Counter
    city_counts = Counter(l.city for l in leads)
    print("\n  City breakdown:")
    for city, count in city_counts.most_common(10):
        print(f"    {city:<30} {count:>4}")

    print("=" * 60 + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UIG Lead Import — CSV / Excel / JSON → Pipeline DB"
    )
    parser.add_argument("--file", required=True, help="Path to leads file (CSV/XLSX/JSON)")
    parser.add_argument("--city", default="Delhi NCR", help="Default city for leads missing city")
    parser.add_argument("--state", default="Delhi", help="Default state")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, no DB writes")
    parser.add_argument("--score", action="store_true", help="AI-score leads after import")
    parser.add_argument("--batch", type=int, default=50, help="DB batch insert size")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        log.error(f"File not found: {path}")
        sys.exit(1)

    log.info(f"Loading: {path} ({path.stat().st_size // 1024} KB)")
    rows = load_file(path)
    log.info(f"Loaded {len(rows)} rows")

    if not rows:
        log.warning("File is empty or unreadable.")
        sys.exit(0)

    defaults = {"city": args.city, "state": args.state}
    leads = parse_all_rows(rows, defaults)
    log.info(f"Parsed {len(leads)} lead records")

    if args.dry_run:
        print_summary(leads)
        log.info("DRY RUN complete — no data written.")
        return

    log.info("Inserting into database...")
    stats = insert_leads(leads, batch_size=args.batch)
    print_summary(leads, stats)

    if args.score and stats["inserted"] > 0:
        score_imported_leads()

    log.info("Import complete.")


if __name__ == "__main__":
    main()
