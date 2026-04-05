"""
All major Indian airports with coordinates, city context, and acquisition zone data.
UIG targets a 5km radius from each airport for priority property acquisition.

LPI Certification Context:
    UIG operates a private earth-mapping satellite division that issues LPI
    (LiDAR Property Identifier) certificates for every 10x10m land parcel on Earth.
    Airport-adjacent properties require mandatory LPI verification before any
    transaction can proceed — positioning UIG as both the certifying authority
    AND the acquirer, creating a powerful market-entry advantage.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class AirportZone:
    iata_code: str
    airport_name: str
    city: str
    state: str
    latitude: float
    longitude: float
    radius_km: float = 5.0
    tier: str = "metro"                # metro | tier1 | tier2 | tier3
    market_type: str = "mixed"         # residential | commercial | industrial | mixed
    avg_price_per_sqft_inr: int = 0    # estimated average
    priority_rank: int = 99            # 1 = highest acquisition priority
    lpi_coverage_pct: float = 100.0    # % of zone already LPI-certified by UIG
    notes: str = ""


# =============================================================================
# TIER 1 METRO AIRPORTS — Highest acquisition priority
# =============================================================================
AIRPORTS: List[AirportZone] = [

    # ── DELHI NCR ─────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="DEL",
        airport_name="Indira Gandhi International Airport",
        city="New Delhi",
        state="Delhi",
        latitude=28.5562,
        longitude=77.1000,
        tier="metro",
        market_type="mixed",
        avg_price_per_sqft_inr=18000,
        priority_rank=1,
        lpi_coverage_pct=100.0,
        notes="Aerocity, Dwarka, Mahipalpur — highest commercial demand. "
              "DLF Cyber City 8km. UIG flagship acquisition zone.",
    ),

    # ── MUMBAI ────────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="BOM",
        airport_name="Chhatrapati Shivaji Maharaj International Airport",
        city="Mumbai",
        state="Maharashtra",
        latitude=19.0896,
        longitude=72.8656,
        tier="metro",
        market_type="mixed",
        avg_price_per_sqft_inr=35000,
        priority_rank=2,
        lpi_coverage_pct=100.0,
        notes="Andheri, Vile Parle, Santa Cruz — premium residential + BKC corridor. "
              "Highest price-per-sqft in India.",
    ),

    # ── BENGALURU ────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="BLR",
        airport_name="Kempegowda International Airport",
        city="Bengaluru",
        state="Karnataka",
        latitude=13.1986,
        longitude=77.7066,
        tier="metro",
        market_type="commercial",
        avg_price_per_sqft_inr=9500,
        priority_rank=3,
        lpi_coverage_pct=100.0,
        notes="Devanahalli IT corridor, Aerospace SEZ. Fastest-growing micro-market. "
              "Prestige and Embassy IT parks nearby.",
    ),

    # ── CHENNAI ───────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="MAA",
        airport_name="Chennai International Airport",
        city="Chennai",
        state="Tamil Nadu",
        latitude=12.9941,
        longitude=80.1709,
        tier="metro",
        market_type="mixed",
        avg_price_per_sqft_inr=8500,
        priority_rank=4,
        lpi_coverage_pct=100.0,
        notes="Pallavaram, Chromepet, Meenambakkam — mixed use. "
              "Heavy manufacturing + IT mix.",
    ),

    # ── HYDERABAD ─────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="HYD",
        airport_name="Rajiv Gandhi International Airport",
        city="Hyderabad",
        state="Telangana",
        latitude=17.2313,
        longitude=78.4298,
        tier="metro",
        market_type="commercial",
        avg_price_per_sqft_inr=7200,
        priority_rank=5,
        lpi_coverage_pct=100.0,
        notes="Shamshabad, Rajendra Nagar — Fab City, Pharma City corridor. "
              "High commercial growth.",
    ),

    # ── KOLKATA ───────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="CCU",
        airport_name="Netaji Subhas Chandra Bose International Airport",
        city="Kolkata",
        state="West Bengal",
        latitude=22.6547,
        longitude=88.4467,
        tier="metro",
        market_type="mixed",
        avg_price_per_sqft_inr=6500,
        priority_rank=6,
        lpi_coverage_pct=100.0,
        notes="Dumdum, Jessore Road, New Town Rajarhat — eastern growth corridor.",
    ),

    # ==========================================================================
    # TIER 1 CITIES (Major business hubs)
    # ==========================================================================

    # ── PUNE ──────────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="PNQ",
        airport_name="Pune International Airport",
        city="Pune",
        state="Maharashtra",
        latitude=18.5822,
        longitude=73.9197,
        tier="tier1",
        market_type="mixed",
        avg_price_per_sqft_inr=9000,
        priority_rank=7,
        lpi_coverage_pct=100.0,
        notes="Lohegaon, Kalyani Nagar, Viman Nagar — IT + education hub. "
              "High young professional demand.",
    ),

    # ── AHMEDABAD ─────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="AMD",
        airport_name="Sardar Vallabhbhai Patel International Airport",
        city="Ahmedabad",
        state="Gujarat",
        latitude=23.0772,
        longitude=72.6347,
        tier="tier1",
        market_type="industrial",
        avg_price_per_sqft_inr=6000,
        priority_rank=8,
        lpi_coverage_pct=100.0,
        notes="GIFT City 15km. DMIC corridor. Gujarat International Finance Tec-City.",
    ),

    # ── KOCHI ─────────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="COK",
        airport_name="Cochin International Airport",
        city="Kochi",
        state="Kerala",
        latitude=10.1520,
        longitude=76.3919,
        tier="tier1",
        market_type="commercial",
        avg_price_per_sqft_inr=7500,
        priority_rank=9,
        lpi_coverage_pct=100.0,
        notes="Nedumbassery, Angamaly — NRI investment hub. "
              "Smart City + IT Park nearby.",
    ),

    # ── GOA (DABOLIM) ─────────────────────────────────────────────────────────
    AirportZone(
        iata_code="GOI",
        airport_name="Goa International Airport (Dabolim)",
        city="Panaji",
        state="Goa",
        latitude=15.3808,
        longitude=73.8314,
        tier="tier1",
        market_type="residential",
        avg_price_per_sqft_inr=12000,
        priority_rank=10,
        lpi_coverage_pct=100.0,
        notes="Vasco, Chicalim, Bogmalo — hospitality, villa, and leisure properties. "
              "NRI and international buyer market.",
    ),

    # ── GOA (MOPA) ────────────────────────────────────────────────────────────
    AirportZone(
        iata_code="GOX",
        airport_name="Manohar International Airport (Mopa)",
        city="Pernem",
        state="Goa",
        latitude=15.7120,
        longitude=73.8690,
        tier="tier1",
        market_type="residential",
        avg_price_per_sqft_inr=14000,
        priority_rank=11,
        lpi_coverage_pct=100.0,
        notes="New airport — emerging premium corridor. North Goa expansion zone. "
              "Highest appreciation potential in Goa.",
    ),

    # ==========================================================================
    # TIER 2 CITIES
    # ==========================================================================

    AirportZone(
        iata_code="JAI",
        airport_name="Jaipur International Airport",
        city="Jaipur",
        state="Rajasthan",
        latitude=26.8242,
        longitude=75.8122,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=5500,
        priority_rank=12,
        notes="Sanganer, Tonk Road — RIICO industrial area. Tourism + textile industry.",
    ),

    AirportZone(
        iata_code="LKO",
        airport_name="Chaudhary Charan Singh International Airport",
        city="Lucknow",
        state="Uttar Pradesh",
        latitude=26.7606,
        longitude=80.8893,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4800,
        priority_rank=13,
        notes="Amausi, Alambagh — UP capital, government + commercial hub.",
    ),

    AirportZone(
        iata_code="IXR",
        airport_name="Birsa Munda Airport",
        city="Ranchi",
        state="Jharkhand",
        latitude=23.3143,
        longitude=85.3217,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=3800,
        priority_rank=14,
        notes="Industrial + mining region. Emerging IT hub.",
    ),

    AirportZone(
        iata_code="VTZ",
        airport_name="Visakhapatnam Airport",
        city="Visakhapatnam",
        state="Andhra Pradesh",
        latitude=17.7212,
        longitude=83.2244,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=5200,
        priority_rank=15,
        notes="Steel plant, port city. New AP capital proximity.",
    ),

    AirportZone(
        iata_code="CJB",
        airport_name="Coimbatore International Airport",
        city="Coimbatore",
        state="Tamil Nadu",
        latitude=11.0300,
        longitude=77.0434,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=5000,
        priority_rank=16,
        notes="Peelamedu — textile + engineering manufacturing. "
              "Growing IT presence.",
    ),

    AirportZone(
        iata_code="IXC",
        airport_name="Chandigarh International Airport",
        city="Chandigarh",
        state="Punjab/Haryana",
        latitude=30.6735,
        longitude=76.7885,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=7200,
        priority_rank=17,
        notes="Mohali IT City, Zirakpur — Tricity (Chandigarh+Mohali+Panchkula). "
              "Premium residential demand.",
    ),

    AirportZone(
        iata_code="NAG",
        airport_name="Dr. Babasaheb Ambedkar International Airport",
        city="Nagpur",
        state="Maharashtra",
        latitude=21.0922,
        longitude=79.0472,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=4500,
        priority_rank=18,
        notes="Zero Mile City — MIHAN SEZ, AIIMS, logistics hub. "
              "India's geometric centre.",
    ),

    AirportZone(
        iata_code="IDR",
        airport_name="Devi Ahilya Bai Holkar Airport",
        city="Indore",
        state="Madhya Pradesh",
        latitude=22.7218,
        longitude=75.8011,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=4800,
        priority_rank=19,
        notes="Cleanest city in India 7 years running. "
              "DMIC node, Pharma + IT growth.",
    ),

    AirportZone(
        iata_code="BHO",
        airport_name="Raja Bhoj International Airport",
        city="Bhopal",
        state="Madhya Pradesh",
        latitude=23.2875,
        longitude=77.3374,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4200,
        priority_rank=20,
        notes="State capital. Lake city — premium residential zone.",
    ),

    AirportZone(
        iata_code="PAT",
        airport_name="Jay Prakash Narayan Airport",
        city="Patna",
        state="Bihar",
        latitude=25.5913,
        longitude=85.0880,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4000,
        priority_rank=21,
        notes="Bihar capital. Emerging commercial demand.",
    ),

    AirportZone(
        iata_code="RPR",
        airport_name="Swami Vivekananda Airport",
        city="Raipur",
        state="Chhattisgarh",
        latitude=21.1804,
        longitude=81.7388,
        tier="tier2",
        market_type="industrial",
        avg_price_per_sqft_inr=4000,
        priority_rank=22,
        notes="CG capital. Steel and mining industry hub.",
    ),

    AirportZone(
        iata_code="AMD",  # note: reuse if needed
        airport_name="Srinagar International Airport",
        city="Srinagar",
        state="Jammu & Kashmir",
        latitude=33.9871,
        longitude=74.7742,
        tier="tier2",
        market_type="residential",
        avg_price_per_sqft_inr=5500,
        priority_rank=23,
        notes="J&K — post-article-370 investment surge. "
              "High NRI + domestic tourism demand.",
    ),

    AirportZone(
        iata_code="ATQ",
        airport_name="Sri Guru Ram Dass Jee International Airport",
        city="Amritsar",
        state="Punjab",
        latitude=31.7096,
        longitude=74.7973,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=5200,
        priority_rank=24,
        notes="Heritage + religious tourism. NRI Punjabi diaspora investment target.",
    ),

    AirportZone(
        iata_code="VNS",
        airport_name="Lal Bahadur Shastri International Airport",
        city="Varanasi",
        state="Uttar Pradesh",
        latitude=25.4524,
        longitude=82.8593,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4200,
        priority_rank=25,
        notes="Spiritual tourism capital. PM constituency — heavy infra investment.",
    ),

    AirportZone(
        iata_code="GAU",
        airport_name="Lokpriya Gopinath Bordoloi International Airport",
        city="Guwahati",
        state="Assam",
        latitude=26.1061,
        longitude=91.5859,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4500,
        priority_rank=26,
        notes="Northeast India gateway. Silk route revival. Act East policy hub.",
    ),

    AirportZone(
        iata_code="BBI",
        airport_name="Biju Patnaik International Airport",
        city="Bhubaneswar",
        state="Odisha",
        latitude=20.2444,
        longitude=85.8177,
        tier="tier2",
        market_type="mixed",
        avg_price_per_sqft_inr=4800,
        priority_rank=27,
        notes="Smart City — Info Valley IT park. Steel + mining corridor.",
    ),

    AirportZone(
        iata_code="TRV",
        airport_name="Trivandrum International Airport",
        city="Thiruvananthapuram",
        state="Kerala",
        latitude=8.4821,
        longitude=76.9201,
        tier="tier2",
        market_type="commercial",
        avg_price_per_sqft_inr=6500,
        priority_rank=28,
        notes="Kerala capital. Technopark IT cluster. NRI investment hub.",
    ),

    AirportZone(
        iata_code="SXR",
        airport_name="Sheikh ul-Alam International Airport",
        city="Srinagar",
        state="Jammu & Kashmir",
        latitude=33.9871,
        longitude=74.7742,
        tier="tier2",
        market_type="residential",
        avg_price_per_sqft_inr=5500,
        priority_rank=29,
        notes="Post-370 investment surge zone.",
    ),
]

# Index airports by IATA code for fast lookup
AIRPORT_INDEX: Dict[str, AirportZone] = {a.iata_code: a for a in AIRPORTS}

# City → Airport mapping (city name → list of airport IATA codes)
CITY_AIRPORTS: Dict[str, List[str]] = {}
for airport in AIRPORTS:
    CITY_AIRPORTS.setdefault(airport.city, []).append(airport.iata_code)

# All supported cities for scraper
ALL_CITIES = list({a.city for a in AIRPORTS})

# Priority Tier 1 cities (immediate focus)
PRIORITY_CITIES = [a.city for a in sorted(AIRPORTS, key=lambda x: x.priority_rank) if a.tier == "metro"]

# Airport zone coordinates for geofencing
def get_airport_bbox(iata_code: str, radius_km: float = 5.0) -> Tuple[float, float, float, float]:
    """
    Return approximate bounding box (min_lat, min_lon, max_lat, max_lon)
    for a circle of radius_km around the airport.
    1 degree lat ≈ 111km, 1 degree lon ≈ 111km * cos(lat)
    """
    import math
    airport = AIRPORT_INDEX.get(iata_code)
    if not airport:
        raise ValueError(f"Unknown IATA code: {iata_code}")
    lat, lon = airport.latitude, airport.longitude
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    return (lat - delta_lat, lon - delta_lon, lat + delta_lat, lon + delta_lon)
