"""
LPI Registry — Public-facing certificate lookup and issuance API.

The LPI Registry serves as UIG's primary market-entry instrument:

1. PROPERTY OWNERS: Must obtain an LPI certificate before selling/renting
   any property in a UIG-mapped zone. UIG is the sole issuing authority.

2. BUYERS/DEVELOPERS: Must verify LPI before transacting. UIG's registry
   is the authoritative source.

3. REAL ESTATE AGENTS: Must register with UIG's agent portal to verify
   LPI certificates on behalf of clients. This creates a mandatory
   agent-UIG relationship.

4. BANKS/LENDERS: RBI-aligned guidelines for mortgages require LPI
   verification. (UIG lobbying initiative — partnership track.)

Revenue Model from LPI:
  - Certificate Issuance Fee: ₹15,000 per property (first issue)
  - Annual Renewal: ₹5,000/year
  - Bulk Agent License: ₹2,50,000/year (unlimited verifications)
  - Premium scan (encroachment + legal overlay): ₹45,000 per property
  - Developer Bundle (10+ properties): ₹1,00,000 flat
"""
import json
import logging
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class LPIRegistryEntry:
    lpi_code: str
    certificate_id: str
    property_address: str
    owner_name: str
    city: str
    state: str
    latitude: float
    longitude: float
    area_sqm: float
    issued_at: str
    valid_until: str
    status: str
    in_airport_zone: bool
    airport_distance_km: Optional[float]
    flags: List[str]
    issuing_officer: str = "UIG Satellite Mapping Division"


class LPIRegistry:
    """
    In-memory LPI registry (production: backed by PostgreSQL + Redis cache).
    Provides certificate issuance, lookup, and verification services.
    """

    def __init__(self):
        self._registry: dict = {}  # cert_id → LPIRegistryEntry
        self._lpi_index: dict = {}  # lpi_code → cert_id

    def register_certificate(
        self,
        certificate,  # LPICertificate from certifier.py
    ) -> LPIRegistryEntry:
        """Register a newly issued certificate in the registry."""
        from app.services.lpi.certifier import LPICertificate
        cert: LPICertificate = certificate

        first_parcel = cert.parcels[0] if cert.parcels else None
        entry = LPIRegistryEntry(
            lpi_code=cert.lpi_codes[0] if cert.lpi_codes else "",
            certificate_id=cert.certificate_id,
            property_address=cert.property_address,
            owner_name=cert.owner_name,
            city=first_parcel.city if first_parcel else "",
            state=first_parcel.state_code if first_parcel else "",
            latitude=first_parcel.latitude if first_parcel else 0,
            longitude=first_parcel.longitude if first_parcel else 0,
            area_sqm=cert.total_area_sqm,
            issued_at=cert.issued_at.isoformat(),
            valid_until=cert.valid_until.isoformat(),
            status=cert.status,
            in_airport_zone=first_parcel.in_airport_zone if first_parcel else False,
            airport_distance_km=first_parcel.airport_distance_km if first_parcel else None,
            flags=cert.flags,
        )

        self._registry[cert.certificate_id] = entry
        for lpi_code in cert.lpi_codes:
            self._lpi_index[lpi_code] = cert.certificate_id

        logger.info(f"LPI registered: {cert.certificate_id} — {cert.property_address}")
        return entry

    def lookup_by_lpi_code(self, lpi_code: str) -> Optional[LPIRegistryEntry]:
        cert_id = self._lpi_index.get(lpi_code)
        if cert_id:
            return self._registry.get(cert_id)
        return None

    def lookup_by_cert_id(self, cert_id: str) -> Optional[LPIRegistryEntry]:
        return self._registry.get(cert_id)

    def lookup_by_address(self, address: str) -> List[LPIRegistryEntry]:
        addr_lower = address.lower()
        return [
            entry for entry in self._registry.values()
            if addr_lower in entry.property_address.lower()
        ]

    def get_certificates_for_city(
        self, city: str, in_airport_zone_only: bool = False
    ) -> List[LPIRegistryEntry]:
        results = [e for e in self._registry.values() if e.city == city]
        if in_airport_zone_only:
            results = [e for e in results if e.in_airport_zone]
        return results

    def issue_and_register(
        self,
        latitude: float,
        longitude: float,
        property_area_sqm: float,
        property_address: str,
        owner_name: str,
        state: str,
        city: str,
        locality: str = "",
    ) -> tuple:
        """One-call convenience: issue certificate + register it. Returns (cert, entry)."""
        from app.services.lpi.certifier import issue_certificate
        cert = issue_certificate(
            latitude=latitude,
            longitude=longitude,
            property_area_sqm=property_area_sqm,
            property_address=property_address,
            owner_name=owner_name,
            state=state,
            city=city,
            locality=locality,
        )
        entry = self.register_certificate(cert)
        return cert, entry

    def to_dict(self) -> dict:
        return {
            "total_certificates": len(self._registry),
            "total_parcels_indexed": len(self._lpi_index),
            "certificates": [asdict(e) for e in self._registry.values()],
        }


# Singleton registry instance
_registry_instance: Optional[LPIRegistry] = None


def get_registry() -> LPIRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = LPIRegistry()
    return _registry_instance
