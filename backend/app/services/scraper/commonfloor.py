"""CommonFloor scraper."""
import time
import logging
from typing import List, Optional
from app.services.scraper.base_scraper import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)


class CommonFloorScraper(BaseScraper):
    portal_name = "commonfloor"
    base_url = "https://www.commonfloor.com"
    rate_limit_seconds = 3.0

    SEARCH_URL = "https://www.commonfloor.com/api/search/v2/listings"

    def scrape(
        self,
        location: str = "Delhi NCR",
        transaction_type: str = "buy",
        property_type: Optional[str] = None,
        max_pages: int = 5,
    ) -> List[ScrapedProperty]:
        results: List[ScrapedProperty] = []
        trans_type = "sale" if transaction_type == "buy" else "rent"

        for page in range(1, max_pages + 1):
            try:
                params = {
                    "city": "delhi",
                    "listing_type": trans_type,
                    "page": page,
                    "per_page": 20,
                    "posted_by": "owner",
                }
                resp = self._client.get(self.SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning(f"CommonFloor returned {resp.status_code} on page {page}")
                    break

                data = resp.json()
                listings = data.get("listings", []) or data.get("data", [])
                if not listings:
                    break

                for raw in listings:
                    prop = self._parse_listing(raw)
                    if prop:
                        results.append(prop)

                logger.info(f"CommonFloor page {page}: {len(listings)} listings")
                time.sleep(self.rate_limit_seconds)

            except Exception as exc:
                logger.error(f"CommonFloor error page {page}: {exc}")
                break

        return results

    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        try:
            prop_id = raw.get("id") or raw.get("listing_id", "")
            listing_url = f"{self.base_url}/listing/{prop_id}" if prop_id else ""

            contact = raw.get("contact") or {}
            owner_name = contact.get("name") or raw.get("owner_name")
            owner_phone = self._normalize_phone(contact.get("phone") or raw.get("phone", ""))

            try:
                price = float(str(raw.get("price", 0)).replace(",", "").replace("₹", "").strip())
            except (ValueError, TypeError):
                price = None

            return ScrapedProperty(
                source_portal=self.portal_name,
                listing_url=listing_url,
                title=raw.get("title", ""),
                property_type=raw.get("property_type", ""),
                transaction_type="rent" if raw.get("listing_type") == "rent" else "buy",
                price=price,
                area_sqft=raw.get("area"),
                locality=raw.get("locality"),
                city=raw.get("city", "Delhi"),
                pincode=raw.get("pincode"),
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_email=contact.get("email"),
                owner_whatsapp=owner_phone,
                listing_date=None,
                raw_data=raw,
            )
        except Exception as exc:
            logger.warning(f"CommonFloor parse error: {exc}")
            return None
