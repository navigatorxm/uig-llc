"""NoBroker scraper — owner-direct listings, high contact quality."""
import time
import logging
from typing import List, Optional
from datetime import datetime
from app.services.scraper.base_scraper import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)


class NoBrokerScraper(BaseScraper):
    portal_name = "nobroker"
    base_url = "https://www.nobroker.in"
    rate_limit_seconds = 3.0

    # NoBroker's listing search API
    SEARCH_URL = "https://www.nobroker.in/api/v1/search/property/list"

    CITY_MAP = {
        "Delhi NCR": "delhi",
        "Delhi": "delhi",
        "Gurgaon": "gurugram",
        "Noida": "noida",
    }

    def scrape(
        self,
        location: str = "Delhi NCR",
        transaction_type: str = "buy",
        property_type: Optional[str] = None,
        max_pages: int = 5,
    ) -> List[ScrapedProperty]:
        results: List[ScrapedProperty] = []
        city = self.CITY_MAP.get(location, "delhi")
        search_type = "SELL" if transaction_type == "buy" else "RENT"

        for page in range(0, max_pages):
            try:
                params = {
                    "city": city,
                    "listingType": search_type,
                    "pageNo": page,
                    "pageSize": 20,
                }
                resp = self._client.get(self.SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning(f"NoBroker returned {resp.status_code} on page {page}")
                    break

                data = resp.json()
                listings = (
                    data.get("data", {}).get("propertyList", [])
                    or data.get("properties", [])
                    or []
                )
                if not listings:
                    break

                for raw in listings:
                    prop = self._parse_listing(raw)
                    if prop:
                        results.append(prop)

                logger.info(f"NoBroker page {page}: {len(listings)} listings")
                time.sleep(self.rate_limit_seconds)

            except Exception as exc:
                logger.error(f"NoBroker error on page {page}: {exc}")
                break

        return results

    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        try:
            slug = raw.get("propertyCode") or raw.get("id", "")
            listing_url = f"{self.base_url}/property-for-sale/{slug}" if slug else ""

            owner_name = raw.get("ownerName") or raw.get("landlordName")
            owner_phone = self._normalize_phone(raw.get("mobileNo") or raw.get("mobile", ""))

            try:
                price = float(str(raw.get("expectedPrice") or raw.get("price", 0)).replace(",", ""))
            except (ValueError, TypeError):
                price = None

            return ScrapedProperty(
                source_portal=self.portal_name,
                listing_url=listing_url,
                title=raw.get("propertyTitle") or raw.get("title", ""),
                property_type=raw.get("propertyType", "").lower().replace(" ", "_"),
                transaction_type="rent" if raw.get("listingType") == "RENT" else "buy",
                price=price,
                area_sqft=raw.get("builtUpArea") or raw.get("area"),
                locality=raw.get("locality") or raw.get("localityName"),
                city=raw.get("city", "Delhi").title(),
                pincode=raw.get("pincode"),
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_email=raw.get("email"),
                owner_whatsapp=owner_phone,
                listing_date=None,
                raw_data=raw,
            )
        except Exception as exc:
            logger.warning(f"NoBroker parse error: {exc}")
            return None
