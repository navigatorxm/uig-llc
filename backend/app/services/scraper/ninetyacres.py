"""99acres.com scraper — uses their internal JSON API endpoints."""
import time
import logging
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.scraper.base_scraper import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)


class NinetyAcresScraper(BaseScraper):
    portal_name = "99acres"
    base_url = "https://www.99acres.com"
    rate_limit_seconds = 3.0

    # Internal search API (JSON)
    SEARCH_URL = "https://www.99acres.com/api/v1/search"

    # Location codes for Delhi NCR
    LOCATION_MAP = {
        "Delhi NCR": "3390",
        "Delhi": "3390",
        "Gurgaon": "3347",
        "Noida": "3426",
        "Faridabad": "3304",
        "Ghaziabad": "3321",
    }

    PROPERTY_TYPE_MAP = {
        "apartment": "1",
        "villa": "3",
        "plot": "5",
        "commercial": "7",
        "independent_house": "2",
    }

    def scrape(
        self,
        location: str = "Delhi NCR",
        transaction_type: str = "buy",
        property_type: Optional[str] = None,
        max_pages: int = 5,
    ) -> List[ScrapedProperty]:
        results: List[ScrapedProperty] = []
        location_id = self.LOCATION_MAP.get(location, "3390")
        res_or_sale = "R" if transaction_type == "rent" else "S"

        for page in range(1, max_pages + 1):
            try:
                params = {
                    "city": location_id,
                    "res_or_sale": res_or_sale,
                    "property_type": self.PROPERTY_TYPE_MAP.get(property_type or "", ""),
                    "page": page,
                    "prefer": "U",  # owner listings
                    "postedby": "1",  # owners only
                }
                resp = self._client.get(self.SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning(f"99acres returned {resp.status_code} on page {page}")
                    break

                data = resp.json()
                listings = data.get("data", {}).get("properties", [])
                if not listings:
                    break

                for raw in listings:
                    prop = self._parse_listing(raw)
                    if prop:
                        results.append(prop)

                logger.info(f"99acres page {page}: scraped {len(listings)} listings")
                time.sleep(self.rate_limit_seconds)

            except Exception as exc:
                logger.error(f"99acres scrape error on page {page}: {exc}")
                break

        return results

    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        try:
            url_key = raw.get("property_url") or raw.get("slug", "")
            listing_url = f"{self.base_url}/{url_key}" if url_key else None

            # 99acres nests contact under "contact" or "owner"
            contact = raw.get("contact") or raw.get("owner") or {}
            owner_name = contact.get("name") or raw.get("owner_name")
            owner_phone = self._normalize_phone(contact.get("phone") or raw.get("phone", ""))
            owner_email = contact.get("email") or raw.get("email")

            price_raw = raw.get("price") or raw.get("listing_price", 0)
            try:
                price = float(str(price_raw).replace(",", "").replace("₹", "").strip())
            except (ValueError, TypeError):
                price = None

            return ScrapedProperty(
                source_portal=self.portal_name,
                listing_url=listing_url or "",
                title=raw.get("title") or raw.get("property_name", ""),
                property_type=raw.get("property_type_label", "").lower().replace(" ", "_"),
                transaction_type="rent" if raw.get("res_or_sale") == "R" else "buy",
                price=price,
                area_sqft=raw.get("area") or raw.get("carpet_area"),
                locality=raw.get("locality_name") or raw.get("area_name"),
                city=raw.get("city_name", "Delhi"),
                pincode=raw.get("pincode"),
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_email=owner_email,
                owner_whatsapp=owner_phone,
                listing_date=self._parse_date(raw.get("updated_date") or raw.get("posted_date")),
                raw_data=raw,
            )
        except Exception as exc:
            logger.warning(f"99acres parse error: {exc}")
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None
