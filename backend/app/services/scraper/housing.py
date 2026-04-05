"""Housing.com scraper."""
import time
import logging
from typing import List, Optional
from app.services.scraper.base_scraper import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)


class HousingScraper(BaseScraper):
    portal_name = "housing"
    base_url = "https://housing.com"
    rate_limit_seconds = 3.0

    SEARCH_URL = "https://housing.com/api/v2/property_listing"

    CITY_MAP = {
        "Delhi NCR": "delhi",
        "Delhi": "delhi",
        "Gurgaon": "gurgaon",
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
        listing_type = "buy" if transaction_type == "buy" else "rent"

        for page in range(1, max_pages + 1):
            try:
                params = {
                    "city": city,
                    "listing_type": listing_type,
                    "page": page,
                    "per_page": 30,
                    "owner_only": "true",
                }
                resp = self._client.get(self.SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning(f"Housing.com returned {resp.status_code} on page {page}")
                    break

                data = resp.json()
                listings = data.get("data", {}).get("listings", []) or data.get("listings", [])
                if not listings:
                    break

                for raw in listings:
                    prop = self._parse_listing(raw)
                    if prop:
                        results.append(prop)

                logger.info(f"Housing.com page {page}: {len(listings)} listings")
                time.sleep(self.rate_limit_seconds)

            except Exception as exc:
                logger.error(f"Housing.com error page {page}: {exc}")
                break

        return results

    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        try:
            prop_id = raw.get("id") or raw.get("listing_id", "")
            listing_url = f"{self.base_url}/in/buy/property-sale/{prop_id}" if prop_id else ""

            owner = raw.get("owner") or raw.get("contact") or {}
            owner_name = owner.get("name") or raw.get("owner_name")
            owner_phone = self._normalize_phone(owner.get("phone") or raw.get("phone", ""))

            try:
                price = float(str(raw.get("price", {}).get("value") or raw.get("price", 0)).replace(",", ""))
            except (ValueError, TypeError):
                price = None

            return ScrapedProperty(
                source_portal=self.portal_name,
                listing_url=listing_url,
                title=raw.get("name") or raw.get("title", ""),
                property_type=raw.get("sub_type") or raw.get("property_type", ""),
                transaction_type="rent" if raw.get("listing_type") == "rent" else "buy",
                price=price,
                area_sqft=raw.get("size") or raw.get("carpet_area"),
                locality=raw.get("locality", {}).get("name") if isinstance(raw.get("locality"), dict) else raw.get("locality"),
                city=raw.get("city", "Delhi"),
                pincode=raw.get("pincode"),
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_email=owner.get("email"),
                owner_whatsapp=owner_phone,
                listing_date=None,
                raw_data=raw,
            )
        except Exception as exc:
            logger.warning(f"Housing.com parse error: {exc}")
            return None
