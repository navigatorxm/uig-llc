"""MagicBricks scraper — uses their internal search API."""
import time
import logging
from typing import List, Optional
from datetime import datetime
from app.services.scraper.base_scraper import BaseScraper, ScrapedProperty

logger = logging.getLogger(__name__)


class MagicBricksScraper(BaseScraper):
    portal_name = "magicbricks"
    base_url = "https://www.magicbricks.com"
    rate_limit_seconds = 3.0

    SEARCH_URL = "https://www.magicbricks.com/mbre-search/sb/getSearchResult"

    CITY_MAP = {
        "Delhi NCR": "CITY-20",
        "Delhi": "CITY-20",
        "Gurgaon": "CITY-35",
        "Noida": "CITY-48",
    }

    def scrape(
        self,
        location: str = "Delhi NCR",
        transaction_type: str = "buy",
        property_type: Optional[str] = None,
        max_pages: int = 5,
    ) -> List[ScrapedProperty]:
        results: List[ScrapedProperty] = []
        city_id = self.CITY_MAP.get(location, "CITY-20")
        prop_type_param = "Multistorey+Apartment,Builder+Floor+Apartment,Penthouse" if not property_type else property_type

        for page in range(1, max_pages + 1):
            try:
                params = {
                    "type": "sale" if transaction_type == "buy" else "rent",
                    "city": city_id,
                    "proptype": prop_type_param,
                    "Pagerequested": page,
                    "pageSize": 30,
                    "postedBy": "0",  # 0 = owners only
                }
                resp = self._client.get(self.SEARCH_URL, params=params, headers=self.headers)
                if resp.status_code != 200:
                    logger.warning(f"MagicBricks returned {resp.status_code} on page {page}")
                    break

                data = resp.json()
                listings = data.get("propertyList", [])
                if not listings:
                    break

                for raw in listings:
                    prop = self._parse_listing(raw)
                    if prop:
                        results.append(prop)

                logger.info(f"MagicBricks page {page}: {len(listings)} listings")
                time.sleep(self.rate_limit_seconds)

            except Exception as exc:
                logger.error(f"MagicBricks error on page {page}: {exc}")
                break

        return results

    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        try:
            listing_url = raw.get("url") or raw.get("propUrl", "")
            if listing_url and not listing_url.startswith("http"):
                listing_url = self.base_url + listing_url

            contact = raw.get("contactDetails") or {}
            owner_name = contact.get("ownerName") or raw.get("ownerName")
            owner_phone = self._normalize_phone(contact.get("mobile") or raw.get("mobile", ""))

            try:
                price = float(str(raw.get("price", 0)).replace(",", "").replace("₹", "").strip())
            except (ValueError, TypeError):
                price = None

            return ScrapedProperty(
                source_portal=self.portal_name,
                listing_url=listing_url,
                title=raw.get("headline") or raw.get("title", ""),
                property_type=raw.get("propType", "").lower().replace(" ", "_"),
                transaction_type="rent" if raw.get("type") == "rent" else "buy",
                price=price,
                area_sqft=raw.get("area") or raw.get("builtUpArea"),
                locality=raw.get("localityName") or raw.get("locality"),
                city=raw.get("cityName", "Delhi"),
                pincode=raw.get("pinCode"),
                owner_name=owner_name,
                owner_phone=owner_phone,
                owner_email=contact.get("email"),
                owner_whatsapp=owner_phone,
                listing_date=None,
                raw_data=raw,
            )
        except Exception as exc:
            logger.warning(f"MagicBricks parse error: {exc}")
            return None
