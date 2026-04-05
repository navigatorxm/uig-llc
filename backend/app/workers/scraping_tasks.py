"""Celery tasks for scraping real estate portals."""
import logging
from typing import Optional
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.lead import Lead, PipelineStage
from app.services.scraper.data_cleaner import deduplicate, to_db_model

logger = logging.getLogger(__name__)

SCRAPER_MAP = {
    "99acres": "app.services.scraper.ninetyacres.NinetyAcresScraper",
    "magicbricks": "app.services.scraper.magicbricks.MagicBricksScraper",
    "nobroker": "app.services.scraper.nobroker.NoBrokerScraper",
    "housing": "app.services.scraper.housing.HousingScraper",
    "commonfloor": "app.services.scraper.commonfloor.CommonFloorScraper",
}


def _load_scraper(portal: str):
    import importlib
    module_path, class_name = SCRAPER_MAP[portal].rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_portal(
    self,
    portal: str,
    location: str = "Delhi NCR",
    transaction_type: str = "buy",
    property_type: Optional[str] = None,
    max_pages: int = 5,
) -> dict:
    """Scrape a portal and persist new property listings + auto-create leads."""
    logger.info(f"Starting scrape: portal={portal}, location={location}, type={transaction_type}")
    db = SessionLocal()
    try:
        scraper = _load_scraper(portal)
        raw_listings = scraper.scrape(location, transaction_type, property_type, max_pages)
        scraper.close()

        unique_listings = deduplicate(raw_listings, db)
        new_properties = 0
        new_leads = 0

        for scraped in unique_listings:
            prop_model = to_db_model(scraped)

            # Auto-create lead if owner has contact info
            if scraped.owner_phone or scraped.owner_email:
                lead = Lead(
                    owner_name=scraped.owner_name or "Unknown Owner",
                    phone=scraped.owner_phone,
                    email=scraped.owner_email,
                    whatsapp=scraped.owner_whatsapp or scraped.owner_phone,
                    pipeline_stage=PipelineStage.new_lead,
                )
                db.add(lead)
                db.flush()
                prop_model.lead_id = lead.id
                new_leads += 1

            db.add(prop_model)
            new_properties += 1

        db.commit()
        logger.info(f"Scrape complete: {new_properties} properties, {new_leads} leads created")
        return {
            "portal": portal,
            "total_scraped": len(raw_listings),
            "unique": len(unique_listings),
            "new_properties": new_properties,
            "new_leads": new_leads,
        }

    except Exception as exc:
        db.rollback()
        logger.error(f"Scraping failed for {portal}: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()
