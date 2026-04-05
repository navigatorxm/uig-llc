"""Tests for scraper services."""
import pytest
from unittest.mock import patch, MagicMock
from app.services.scraper.base_scraper import ScrapedProperty
from app.services.scraper.ninetyacres import NinetyAcresScraper
from app.services.scraper.data_cleaner import (
    deduplicate, tag_location, classify_budget, to_db_model
)


class TestDataCleaner:
    def test_tag_location_prime(self):
        assert tag_location("South Delhi, Vasant Vihar") == "prime_ncr"

    def test_tag_location_peripheral(self):
        assert tag_location("Noida Sector 62") == "peripheral"

    def test_tag_location_unknown(self):
        assert tag_location("") == "unknown"

    def test_classify_budget_under_50L(self):
        assert classify_budget(4_500_000) == "under_50L"

    def test_classify_budget_1cr_2cr(self):
        assert classify_budget(15_000_000) == "1Cr_2Cr"

    def test_classify_budget_above_5cr(self):
        assert classify_budget(60_000_000) == "above_5Cr"

    def test_deduplicate_removes_url_duplicates(self):
        props = [
            ScrapedProperty(source_portal="99acres", listing_url="https://example.com/1", transaction_type="buy"),
            ScrapedProperty(source_portal="99acres", listing_url="https://example.com/1", transaction_type="buy"),
            ScrapedProperty(source_portal="99acres", listing_url="https://example.com/2", transaction_type="buy"),
        ]
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = deduplicate(props, mock_db)
        assert len(result) == 2

    def test_deduplicate_removes_phone_duplicates(self):
        props = [
            ScrapedProperty(source_portal="99acres", listing_url="url1", transaction_type="buy", owner_phone="+919876543210"),
            ScrapedProperty(source_portal="99acres", listing_url="url2", transaction_type="buy", owner_phone="+919876543210"),
        ]
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = deduplicate(props, mock_db)
        assert len(result) == 1


class TestNinetyAcresScraper:
    def test_normalize_phone_with_0_prefix(self):
        scraper = NinetyAcresScraper()
        assert scraper._normalize_phone("09876543210") == "+919876543210"

    def test_normalize_phone_no_prefix(self):
        scraper = NinetyAcresScraper()
        assert scraper._normalize_phone("9876543210") == "+919876543210"

    def test_normalize_phone_already_has_plus(self):
        scraper = NinetyAcresScraper()
        assert scraper._normalize_phone("+919876543210") == "+919876543210"

    def test_normalize_phone_none(self):
        scraper = NinetyAcresScraper()
        assert scraper._normalize_phone("") is None

    @patch("httpx.Client.get")
    def test_scrape_handles_api_error(self, mock_get):
        mock_get.return_value.status_code = 500
        scraper = NinetyAcresScraper()
        results = scraper.scrape("Delhi NCR", "buy", None, 1)
        assert results == []

    def test_parse_listing_valid(self):
        scraper = NinetyAcresScraper()
        raw = {
            "property_url": "property-for-sale/test",
            "title": "3BHK Apartment",
            "property_type_label": "Apartment",
            "price": "5000000",
            "area": 1200,
            "locality_name": "Vasant Vihar",
            "city_name": "Delhi",
            "contact": {"name": "Rajesh Sharma", "phone": "9876543210"},
        }
        result = scraper._parse_listing(raw)
        assert result is not None
        assert result.owner_name == "Rajesh Sharma"
        assert result.price == 5000000.0
