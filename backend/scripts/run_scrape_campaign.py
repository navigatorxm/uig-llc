#!/usr/bin/env python3
"""
UIG Scrape Campaign Runner
==========================
Triggers fresh property scraping across all priority airport zones,
collects results, and reports statistics.

Usage:
    python scripts/run_scrape_campaign.py
    python scripts/run_scrape_campaign.py --cities DEL BOM BLR
    python scripts/run_scrape_campaign.py --portals 99acres magicbricks nobroker
    python scripts/run_scrape_campaign.py --pages 3 --async
    python scripts/run_scrape_campaign.py --cities DEL --portals nobroker --pages 5

Options:
    --cities    IATA codes to scrape (default: DEL BOM BLR HYD MAA)
    --portals   Portal names to use (default: 99acres magicbricks nobroker housing)
    --pages     Pages per portal per city (default: 2)
    --async     Submit as Celery tasks and exit (non-blocking)
    --wait      When using --async, poll until tasks complete
    --dry-run   Show what would be scraped without making requests
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scrape_campaign")


# ── Airport zone configs ──────────────────────────────────────────────────────

AIRPORT_SEARCH_CONFIG: Dict[str, Dict[str, Any]] = {
    "DEL": {
        "name": "Delhi Indira Gandhi International",
        "city": "Delhi NCR",
        "state": "Delhi",
        "localities": [
            "Mahipalpur", "Dwarka", "Vasant Kunj", "Aerocity",
            "Kapashera", "Rangpuri", "Uttam Nagar", "Palam",
        ],
        "portals": ["99acres", "magicbricks", "nobroker", "housing"],
        "priority": 1,
    },
    "BOM": {
        "name": "Mumbai Chhatrapati Shivaji Maharaj International",
        "city": "Mumbai",
        "state": "Maharashtra",
        "localities": [
            "Andheri", "Kurla", "Santacruz", "Vile Parle",
            "Sakinaka", "Chakala", "BKC", "Powai",
        ],
        "portals": ["99acres", "magicbricks", "nobroker", "housing"],
        "priority": 1,
    },
    "BLR": {
        "name": "Bengaluru Kempegowda International",
        "city": "Bengaluru",
        "state": "Karnataka",
        "localities": [
            "Devanahalli", "Yelahanka", "Hebbal", "Kempapura",
            "Thanisandra", "Jakkur", "Vidyaranyapura", "Nagawara",
        ],
        "portals": ["99acres", "magicbricks", "nobroker"],
        "priority": 1,
    },
    "HYD": {
        "name": "Hyderabad Rajiv Gandhi International",
        "city": "Hyderabad",
        "state": "Telangana",
        "localities": [
            "Shamshabad", "Rajendra Nagar", "Tukkuguda",
            "Adibatla", "Nanakramguda", "Gachibowli",
        ],
        "portals": ["99acres", "magicbricks", "nobroker"],
        "priority": 2,
    },
    "MAA": {
        "name": "Chennai International",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "localities": [
            "Meenambakkam", "Pallavaram", "Tambaram",
            "Perungalathur", "Chromepet", "Guindy",
        ],
        "portals": ["99acres", "magicbricks", "housing"],
        "priority": 2,
    },
    "CCU": {
        "name": "Kolkata Netaji Subhas Chandra Bose International",
        "city": "Kolkata",
        "state": "West Bengal",
        "localities": [
            "Dum Dum", "Rajarhat", "New Town", "Baguiati",
            "VIP Road", "Jessore Road",
        ],
        "portals": ["99acres", "magicbricks"],
        "priority": 2,
    },
    "PNQ": {
        "name": "Pune International",
        "city": "Pune",
        "state": "Maharashtra",
        "localities": [
            "Viman Nagar", "Lohegaon", "Kalyani Nagar",
            "Nagar Road", "Wagholi", "Kharadi",
        ],
        "portals": ["99acres", "nobroker", "magicbricks"],
        "priority": 2,
    },
    "AMD": {
        "name": "Ahmedabad Sardar Vallabhbhai Patel International",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "localities": [
            "Hansol", "Chandkheda", "Ranip", "Motera",
            "GIFT City", "Sector 1",
        ],
        "portals": ["99acres", "magicbricks"],
        "priority": 3,
    },
    "GOI": {
        "name": "Goa Dabolim International",
        "city": "Panaji",
        "state": "Goa",
        "localities": [
            "Dabolim", "Chicalim", "Vasco da Gama",
            "Bogmalo", "Panaji", "Panjim",
        ],
        "portals": ["99acres", "magicbricks"],
        "priority": 3,
    },
    "COK": {
        "name": "Kochi International",
        "city": "Kochi",
        "state": "Kerala",
        "localities": [
            "Nedumbassery", "Angamaly", "Aluva",
            "Edapally", "Kakkanad", "Infopark",
        ],
        "portals": ["99acres", "magicbricks"],
        "priority": 3,
    },
}

PORTAL_CLASSES = {
    "99acres": ("app.services.scraper.ninetyacres", "NinetyAcresScraper"),
    "magicbricks": ("app.services.scraper.magicbricks", "MagicBricksScraper"),
    "nobroker": ("app.services.scraper.nobroker", "NoBrokerScraper"),
    "housing": ("app.services.scraper.housing", "HousingScraper"),
    "commonfloor": ("app.services.scraper.commonfloor", "CommonFloorScraper"),
}


# ── direct (synchronous) scrape ───────────────────────────────────────────────

def run_scrape_direct(
    iata: str,
    config: Dict[str, Any],
    portal_names: List[str],
    pages: int,
) -> Dict[str, Any]:
    """Run scrapers synchronously and insert results into DB."""
    from app.database import SessionLocal
    from app.services.scraper.data_cleaner import deduplicate, tag_location, to_db_model
    from app.models.property import Property
    from app.models.lead import Lead, PipelineStage

    city_results = {
        "iata": iata,
        "city": config["city"],
        "portals_run": [],
        "total_scraped": 0,
        "total_inserted": 0,
        "total_duplicate": 0,
        "errors": [],
    }

    for portal_name in portal_names:
        if portal_name not in PORTAL_CLASSES:
            log.warning(f"Unknown portal: {portal_name}")
            continue

        module_path, class_name = PORTAL_CLASSES[portal_name]
        try:
            import importlib
            module = importlib.import_module(module_path)
            ScraperClass = getattr(module, class_name)
        except (ImportError, AttributeError) as exc:
            log.error(f"Cannot load scraper {portal_name}: {exc}")
            city_results["errors"].append(f"{portal_name}: import error — {exc}")
            continue

        portal_scraped = 0
        portal_inserted = 0
        portal_dupes = 0

        for locality in config["localities"][:4]:  # top 4 localities per city
            search_query = f"{locality} {config['city']}"
            log.info(f"  Scraping {portal_name} → {search_query}")

            try:
                scraper = ScraperClass(
                    city=config["city"],
                    state=config["state"],
                    locality=locality,
                    transaction_type="buy",
                    max_pages=pages,
                )
                raw_listings = scraper.scrape()
            except Exception as exc:
                log.error(f"  Scrape error ({portal_name}/{locality}): {exc}")
                city_results["errors"].append(f"{portal_name}/{locality}: {exc}")
                continue

            if not raw_listings:
                log.info(f"  No listings from {portal_name}/{locality}")
                continue

            portal_scraped += len(raw_listings)

            # dedup + tag
            tagged = [tag_location(prop) for prop in raw_listings]
            deduped = deduplicate(tagged)

            session = SessionLocal()
            try:
                for prop in deduped:
                    # check existing by URL or phone
                    existing = None
                    if prop.listing_url:
                        existing = session.query(Property).filter(
                            Property.listing_url == prop.listing_url
                        ).first()
                    if not existing and prop.owner_phone:
                        existing = session.query(Property).filter(
                            Property.owner_phone == prop.owner_phone
                        ).first()
                    if existing:
                        portal_dupes += 1
                        continue

                    # create lead + property
                    db_lead = Lead(
                        owner_name=prop.owner_name or "Unknown",
                        phone=prop.owner_phone or "",
                        email=prop.owner_email or None,
                        whatsapp=prop.owner_whatsapp or prop.owner_phone or None,
                        pipeline_stage=PipelineStage.new_lead,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(db_lead)
                    session.flush()

                    db_prop = to_db_model(prop, lead_id=db_lead.id)
                    session.add(db_prop)
                    portal_inserted += 1

                session.commit()
            except Exception as exc:
                session.rollback()
                log.error(f"  DB error: {exc}")
                city_results["errors"].append(f"DB error: {exc}")
            finally:
                session.close()

        city_results["portals_run"].append({
            "portal": portal_name,
            "scraped": portal_scraped,
            "inserted": portal_inserted,
            "duplicates": portal_dupes,
        })
        city_results["total_scraped"] += portal_scraped
        city_results["total_inserted"] += portal_inserted
        city_results["total_duplicate"] += portal_dupes

        log.info(
            f"  {portal_name}: {portal_scraped} scraped, "
            f"{portal_inserted} new, {portal_dupes} dupes"
        )

    return city_results


# ── async via Celery ──────────────────────────────────────────────────────────

def run_scrape_async(
    iata: str,
    config: Dict[str, Any],
    portal_names: List[str],
    pages: int,
) -> List[str]:
    """Submit scrape jobs to Celery and return task IDs."""
    try:
        from app.workers.scraping_tasks import scrape_portal
    except ImportError as exc:
        log.error(f"Cannot import Celery tasks: {exc}")
        return []

    task_ids = []
    for portal_name in portal_names:
        for locality in config["localities"][:4]:
            task = scrape_portal.delay(
                portal=portal_name,
                city=config["city"],
                state=config["state"],
                locality=locality,
                transaction_type="buy",
                max_pages=pages,
            )
            task_ids.append(task.id)
            log.info(f"  Queued: {portal_name}/{locality} → task {task.id}")

    return task_ids


def poll_tasks(task_ids: List[str], timeout: int = 300):
    """Poll Celery tasks until all complete or timeout."""
    from celery.result import AsyncResult
    from app.workers.celery_app import celery_app

    log.info(f"Polling {len(task_ids)} tasks (timeout={timeout}s)...")
    deadline = time.time() + timeout
    pending = set(task_ids)

    while pending and time.time() < deadline:
        done = set()
        for tid in pending:
            result = AsyncResult(tid, app=celery_app)
            if result.ready():
                status = "OK" if result.successful() else "FAILED"
                log.info(f"  Task {tid[:12]}... → {status}")
                done.add(tid)
        pending -= done
        if pending:
            time.sleep(5)

    if pending:
        log.warning(f"{len(pending)} tasks did not complete within {timeout}s.")
    else:
        log.info("All tasks completed.")


# ── reporting ─────────────────────────────────────────────────────────────────

def print_campaign_report(results: List[Dict[str, Any]]):
    total_scraped = sum(r["total_scraped"] for r in results)
    total_inserted = sum(r["total_inserted"] for r in results)
    total_dupes = sum(r["total_duplicate"] for r in results)
    all_errors = [e for r in results for e in r.get("errors", [])]

    print("\n" + "=" * 65)
    print("  UIG SCRAPE CAMPAIGN REPORT")
    print("=" * 65)
    print(f"  Cities scraped         : {len(results)}")
    print(f"  Total listings found   : {total_scraped}")
    print(f"  New leads inserted     : {total_inserted}")
    print(f"  Duplicates skipped     : {total_dupes}")
    print(f"  Errors                 : {len(all_errors)}")

    print("\n  City breakdown:")
    print(f"  {'City':<20} {'Scraped':>8} {'New':>8} {'Dupes':>8}")
    print("  " + "-" * 46)
    for r in results:
        print(
            f"  {r['city']:<20} {r['total_scraped']:>8} "
            f"{r['total_inserted']:>8} {r['total_duplicate']:>8}"
        )

    print("\n  Portal breakdown:")
    portal_totals: Dict[str, Dict] = {}
    for r in results:
        for p in r["portals_run"]:
            if p["portal"] not in portal_totals:
                portal_totals[p["portal"]] = {"scraped": 0, "inserted": 0}
            portal_totals[p["portal"]]["scraped"] += p["scraped"]
            portal_totals[p["portal"]]["inserted"] += p["inserted"]

    print(f"  {'Portal':<20} {'Scraped':>8} {'Inserted':>10}")
    print("  " + "-" * 40)
    for portal, totals in portal_totals.items():
        print(f"  {portal:<20} {totals['scraped']:>8} {totals['inserted']:>10}")

    if all_errors:
        print(f"\n  Errors ({len(all_errors)}):")
        for err in all_errors[:10]:
            print(f"    - {err}")
        if len(all_errors) > 10:
            print(f"    ... and {len(all_errors) - 10} more")

    print("=" * 65 + "\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UIG Scrape Campaign — Scrape all airport zones for fresh leads"
    )
    parser.add_argument(
        "--cities",
        nargs="+",
        default=["DEL", "BOM", "BLR", "HYD", "MAA"],
        metavar="IATA",
        help="IATA airport codes to scrape (default: DEL BOM BLR HYD MAA)",
    )
    parser.add_argument(
        "--portals",
        nargs="+",
        default=["99acres", "magicbricks", "nobroker", "housing"],
        help="Portals to scrape",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="Pages per portal per locality (default: 2)",
    )
    parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Submit as Celery tasks (non-blocking)",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="With --async: wait for tasks to complete",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without executing",
    )
    args = parser.parse_args()

    # Validate IATA codes
    invalid = [c for c in args.cities if c not in AIRPORT_SEARCH_CONFIG]
    if invalid:
        log.error(f"Unknown IATA codes: {invalid}")
        log.info(f"Valid codes: {list(AIRPORT_SEARCH_CONFIG.keys())}")
        sys.exit(1)

    if args.dry_run:
        print("\n=== DRY RUN — Scrape Plan ===")
        total_jobs = 0
        for iata in args.cities:
            cfg = AIRPORT_SEARCH_CONFIG[iata]
            portals = [p for p in args.portals if p in cfg["portals"]]
            jobs = len(portals) * min(4, len(cfg["localities"]))
            total_jobs += jobs
            print(f"\n  {iata} — {cfg['city']}")
            print(f"    Portals : {portals}")
            print(f"    Localities (top 4): {cfg['localities'][:4]}")
            print(f"    Pages/job: {args.pages}  |  Jobs: {jobs}")
        print(f"\n  Total scrape jobs: {total_jobs}")
        print(f"  Estimated new leads: ~{total_jobs * 20 * args.pages}\n")
        return

    log.info(
        f"Starting scrape campaign: {len(args.cities)} cities, "
        f"{len(args.portals)} portals, {args.pages} pages each"
    )

    started_at = datetime.utcnow()
    all_results = []
    all_task_ids = []

    for iata in args.cities:
        cfg = AIRPORT_SEARCH_CONFIG[iata]
        portals = [p for p in args.portals if p in cfg["portals"]]
        if not portals:
            log.warning(f"{iata}: no matching portals — skipping")
            continue

        log.info(f"\n{'─' * 50}")
        log.info(f"  City: {cfg['city']} ({iata})")
        log.info(f"  Portals: {portals}")

        if args.use_async:
            task_ids = run_scrape_async(iata, cfg, portals, args.pages)
            all_task_ids.extend(task_ids)
        else:
            result = run_scrape_direct(iata, cfg, portals, args.pages)
            all_results.append(result)

    if args.use_async:
        log.info(f"\nSubmitted {len(all_task_ids)} Celery tasks.")
        if args.wait:
            poll_tasks(all_task_ids, timeout=600)
        else:
            print("\nTask IDs (use Celery Flower or 'celery inspect' to monitor):")
            for tid in all_task_ids:
                print(f"  {tid}")
        return

    elapsed = (datetime.utcnow() - started_at).total_seconds()
    log.info(f"\nCampaign finished in {elapsed:.1f}s")
    print_campaign_report(all_results)

    # Save report to file
    report_path = Path("scrape_campaign_report.json")
    with open(report_path, "w") as f:
        json.dump(
            {
                "run_at": started_at.isoformat(),
                "elapsed_seconds": elapsed,
                "cities": args.cities,
                "portals": args.portals,
                "results": all_results,
            },
            f,
            indent=2,
        )
    log.info(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()
