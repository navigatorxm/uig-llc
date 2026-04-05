from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import httpx
from fake_useragent import UserAgent


@dataclass
class ScrapedProperty:
    source_portal: str
    listing_url: str
    title: Optional[str] = None
    property_type: Optional[str] = None
    transaction_type: str = "buy"
    price: Optional[float] = None
    area_sqft: Optional[float] = None
    address: Optional[str] = None
    locality: Optional[str] = None
    city: str = "Delhi"
    pincode: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    listing_date: Optional[datetime] = None
    raw_data: dict = field(default_factory=dict)


class BaseScraper(ABC):
    """Abstract base class for all real estate portal scrapers."""

    portal_name: str = ""
    base_url: str = ""
    rate_limit_seconds: float = 2.0

    def __init__(self):
        self._ua = UserAgent()
        self._client = httpx.Client(
            headers={"User-Agent": self._ua.random},
            timeout=30.0,
            follow_redirects=True,
        )

    @property
    def headers(self) -> dict:
        return {
            "User-Agent": self._ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }

    @abstractmethod
    def scrape(
        self,
        location: str,
        transaction_type: str,
        property_type: Optional[str],
        max_pages: int,
    ) -> List[ScrapedProperty]:
        """Scrape listings and return a list of ScrapedProperty objects."""
        ...

    @abstractmethod
    def _parse_listing(self, raw: dict) -> Optional[ScrapedProperty]:
        """Parse a single raw listing dict into a ScrapedProperty."""
        ...

    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Strip whitespace and ensure +91 prefix for Indian numbers."""
        if not phone:
            return None
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "+91" + phone[1:]
        elif not phone.startswith("+"):
            phone = "+91" + phone
        return phone if len(phone) >= 10 else None

    def _classify_budget(self, price: Optional[float]) -> str:
        if not price:
            return "unknown"
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

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
