"""
City-specific acquisition configuration for all major Indian cities.
Each config drives scraper settings, outreach tone, legal requirements,
and market intelligence for UIG's acquisition team.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CityAcquisitionConfig:
    city: str
    state: str
    airport_iata: List[str]

    # Scraper settings
    portals_priority: List[str]        # ordered by expected yield
    search_localities: List[str]       # neighbourhoods to target within city

    # Market context
    avg_price_buy_inr_per_sqft: int
    avg_rent_inr_per_sqft_per_month: float
    market_trend: str                  # "rising" | "stable" | "cooling"
    investor_type: str                 # NRI | HNI | institutional | retail
    typical_deal_size_cr: float        # in crores INR

    # Regulatory context
    land_record_authority: str
    lpi_mandate_status: str            # "active" | "pending" | "lobby"
    stamp_duty_pct: float
    registration_charges_pct: float
    known_encroachment_risk: str       # "low" | "moderate" | "high"

    # UIG zone priority
    uig_zone_priority: int             # 1 = highest
    target_property_types: List[str]
    acquisition_goal: str              # "buy" | "rent" | "both"

    # Agent network notes
    top_agent_firms: List[str]
    agent_commission_buy_pct: float    # typical buyer agent commission
    agent_commission_rent_pct: float

    notes: str = ""


CITY_CONFIGS: Dict[str, CityAcquisitionConfig] = {

    # ── DELHI NCR ─────────────────────────────────────────────────────────────
    "New Delhi": CityAcquisitionConfig(
        city="New Delhi",
        state="Delhi",
        airport_iata=["DEL"],
        portals_priority=["99acres", "magicbricks", "nobroker", "housing", "commonfloor"],
        search_localities=[
            "Aerocity", "Mahipalpur", "Dwarka Sector 1", "Dwarka Sector 10",
            "IGI Colony", "Samalkha", "Rangpuri", "Vasant Kunj",
            "Kapashera", "Bijwasan", "Palam Colony",
        ],
        avg_price_buy_inr_per_sqft=18000,
        avg_rent_inr_per_sqft_per_month=45,
        market_trend="rising",
        investor_type="institutional",
        typical_deal_size_cr=3.5,
        land_record_authority="Delhi Land Records, DDA",
        lpi_mandate_status="active",
        stamp_duty_pct=4.0,
        registration_charges_pct=1.0,
        known_encroachment_risk="moderate",
        uig_zone_priority=1,
        target_property_types=["commercial", "plot", "apartment", "warehouse"],
        acquisition_goal="both",
        top_agent_firms=["Anarock", "JLL", "CBRE", "Colliers", "Knight Frank"],
        agent_commission_buy_pct=1.0,
        agent_commission_rent_pct=8.33,
        notes="Aerocity is India's first integrated hospitality district. "
              "Strong demand from airlines, hotels, logistics. LPI mandate fully active.",
    ),

    # ── MUMBAI ────────────────────────────────────────────────────────────────
    "Mumbai": CityAcquisitionConfig(
        city="Mumbai",
        state="Maharashtra",
        airport_iata=["BOM"],
        portals_priority=["magicbricks", "99acres", "housing", "nobroker"],
        search_localities=[
            "Andheri West", "Andheri East", "Vile Parle", "Santa Cruz West",
            "Kalina", "Kurla", "Sahar", "Chakala", "MIDC Andheri",
            "Marol", "Saki Naka",
        ],
        avg_price_buy_inr_per_sqft=35000,
        avg_rent_inr_per_sqft_per_month=90,
        market_trend="stable",
        investor_type="HNI",
        typical_deal_size_cr=8.0,
        land_record_authority="Maharashtra Land Records, IGR",
        lpi_mandate_status="active",
        stamp_duty_pct=5.0,
        registration_charges_pct=1.0,
        known_encroachment_risk="high",
        uig_zone_priority=2,
        target_property_types=["commercial", "apartment", "office"],
        acquisition_goal="both",
        top_agent_firms=["JLL Mumbai", "CBRE Mumbai", "Knight Frank", "Anarock"],
        agent_commission_buy_pct=1.0,
        agent_commission_rent_pct=8.33,
        notes="BKC 3km from airport — premium commercial. Dharavi redevelopment "
              "pipeline. High rental yields in Andheri micro-market.",
    ),

    # ── BENGALURU ────────────────────────────────────────────────────────────
    "Bengaluru": CityAcquisitionConfig(
        city="Bengaluru",
        state="Karnataka",
        airport_iata=["BLR"],
        portals_priority=["nobroker", "99acres", "housing", "magicbricks"],
        search_localities=[
            "Devanahalli", "Bagalur", "Yelahanka", "Thanisandra",
            "Vidyanagar", "Jala Hobli", "Aerospace Park",
            "North Bengaluru", "NH-44 Corridor",
        ],
        avg_price_buy_inr_per_sqft=9500,
        avg_rent_inr_per_sqft_per_month=28,
        market_trend="rising",
        investor_type="institutional",
        typical_deal_size_cr=2.5,
        land_record_authority="Karnataka Revenue Department, BBMP",
        lpi_mandate_status="active",
        stamp_duty_pct=5.6,
        registration_charges_pct=1.0,
        known_encroachment_risk="low",
        uig_zone_priority=3,
        target_property_types=["plot", "commercial", "warehouse", "apartment"],
        acquisition_goal="buy",
        top_agent_firms=["Square Yards", "Brigade", "Prestige Agents", "JLL Bengaluru"],
        agent_commission_buy_pct=1.0,
        agent_commission_rent_pct=8.33,
        notes="Aerospace SEZ adjacent. IT/aerospace corridor boom. "
              "Land plots near airport at 3x appreciation vs. 5 years ago.",
    ),

    # ── CHENNAI ───────────────────────────────────────────────────────────────
    "Chennai": CityAcquisitionConfig(
        city="Chennai",
        state="Tamil Nadu",
        airport_iata=["MAA"],
        portals_priority=["99acres", "magicbricks", "housing"],
        search_localities=[
            "Pallavaram", "Chromepet", "Meenambakkam", "Tirusulam",
            "Perungalathur", "Vandalur", "Alandur", "St. Thomas Mount",
        ],
        avg_price_buy_inr_per_sqft=8500,
        avg_rent_inr_per_sqft_per_month=22,
        market_trend="stable",
        investor_type="retail",
        typical_deal_size_cr=1.8,
        land_record_authority="Tamil Nadu Registration Dept, CMDA",
        lpi_mandate_status="pending",
        stamp_duty_pct=7.0,
        registration_charges_pct=4.0,
        known_encroachment_risk="moderate",
        uig_zone_priority=4,
        target_property_types=["plot", "independent_house", "apartment"],
        acquisition_goal="both",
        top_agent_firms=["TVH", "Casagrand Agents", "CBRE Chennai"],
        agent_commission_buy_pct=1.5,
        agent_commission_rent_pct=8.33,
        notes="Manufacturing-heavy. Tamil Nadu IND corridor adjacent. "
              "Strong South Chennai IT belt overlap.",
    ),

    # ── HYDERABAD ─────────────────────────────────────────────────────────────
    "Hyderabad": CityAcquisitionConfig(
        city="Hyderabad",
        state="Telangana",
        airport_iata=["HYD"],
        portals_priority=["99acres", "magicbricks", "nobroker"],
        search_localities=[
            "Shamshabad", "Rajendra Nagar", "Bandlaguda", "Mehmood Nagar",
            "Tukkuguda", "Pedda Amberpet", "Fab City",
            "Pharma City Corridor", "Adibatla IT Park",
        ],
        avg_price_buy_inr_per_sqft=7200,
        avg_rent_inr_per_sqft_per_month=20,
        market_trend="rising",
        investor_type="institutional",
        typical_deal_size_cr=2.2,
        land_record_authority="Telangana Registration & Stamps, HMDA",
        lpi_mandate_status="active",
        stamp_duty_pct=4.0,
        registration_charges_pct=0.5,
        known_encroachment_risk="low",
        uig_zone_priority=5,
        target_property_types=["plot", "warehouse", "commercial", "apartment"],
        acquisition_goal="buy",
        top_agent_firms=["Anarock Hyderabad", "Cushman & Wakefield", "JLL HYD"],
        agent_commission_buy_pct=1.0,
        agent_commission_rent_pct=8.33,
        notes="Hyderabad fastest-growing metro in India. ORR-airport zone. "
              "Pharma City + Data Centre cluster. Lowest stamp duty in India.",
    ),

    # ── KOLKATA ───────────────────────────────────────────────────────────────
    "Kolkata": CityAcquisitionConfig(
        city="Kolkata",
        state="West Bengal",
        airport_iata=["CCU"],
        portals_priority=["99acres", "magicbricks"],
        search_localities=[
            "Dum Dum", "Nager Bazar", "Nagerbazar", "Jessore Road",
            "VIP Road", "New Town Rajarhat", "Action Area I",
        ],
        avg_price_buy_inr_per_sqft=6500,
        avg_rent_inr_per_sqft_per_month=18,
        market_trend="stable",
        investor_type="retail",
        typical_deal_size_cr=1.5,
        land_record_authority="West Bengal Land Records, KMDA",
        lpi_mandate_status="pending",
        stamp_duty_pct=5.0,
        registration_charges_pct=1.0,
        known_encroachment_risk="moderate",
        uig_zone_priority=6,
        target_property_types=["apartment", "plot", "commercial"],
        acquisition_goal="both",
        top_agent_firms=["Merlin Group Agents", "PS Group", "Ambuja Realty"],
        agent_commission_buy_pct=2.0,
        agent_commission_rent_pct=8.33,
        notes="Eastern India gateway. New Town IT hub adjacent. "
              "Airport Zone + Rajarhat new township overlap.",
    ),

    # ── PUNE ──────────────────────────────────────────────────────────────────
    "Pune": CityAcquisitionConfig(
        city="Pune",
        state="Maharashtra",
        airport_iata=["PNQ"],
        portals_priority=["nobroker", "99acres", "magicbricks"],
        search_localities=[
            "Lohegaon", "Viman Nagar", "Kalyani Nagar", "Wadgaon Sheri",
            "Dhanori", "Vishrantwadi", "Alandi Road",
        ],
        avg_price_buy_inr_per_sqft=9000,
        avg_rent_inr_per_sqft_per_month=25,
        market_trend="rising",
        investor_type="retail",
        typical_deal_size_cr=1.8,
        land_record_authority="Maharashtra Land Records, PCMC/PMC",
        lpi_mandate_status="active",
        stamp_duty_pct=5.0,
        registration_charges_pct=1.0,
        known_encroachment_risk="low",
        uig_zone_priority=7,
        target_property_types=["apartment", "villa", "plot"],
        acquisition_goal="both",
        top_agent_firms=["Anarock Pune", "Knight Frank Pune"],
        agent_commission_buy_pct=1.5,
        agent_commission_rent_pct=8.33,
        notes="IT + education hub. Viman Nagar is premium micro-market. "
              "Pune-Mumbai Expressway connectivity premium.",
    ),

    # ── AHMEDABAD ─────────────────────────────────────────────────────────────
    "Ahmedabad": CityAcquisitionConfig(
        city="Ahmedabad",
        state="Gujarat",
        airport_iata=["AMD"],
        portals_priority=["magicbricks", "99acres", "housing"],
        search_localities=[
            "Hansol", "Chandlodia", "Randesan", "Motera",
            "Tragad", "Gota", "Sabarmati",
        ],
        avg_price_buy_inr_per_sqft=6000,
        avg_rent_inr_per_sqft_per_month=16,
        market_trend="rising",
        investor_type="institutional",
        typical_deal_size_cr=1.5,
        land_record_authority="Gujarat State Land Records, AMC/AUDA",
        lpi_mandate_status="active",
        stamp_duty_pct=4.9,
        registration_charges_pct=1.0,
        known_encroachment_risk="low",
        uig_zone_priority=8,
        target_property_types=["industrial", "plot", "commercial"],
        acquisition_goal="buy",
        top_agent_firms=["Anarock Gujarat", "CBRE Ahmedabad"],
        agent_commission_buy_pct=1.5,
        agent_commission_rent_pct=8.33,
        notes="GIFT City 15km. Gujarat is FDI-friendly. DMIC corridor. "
              "Industrial plots near airport highly strategic.",
    ),

    # ── KOCHI ─────────────────────────────────────────────────────────────────
    "Kochi": CityAcquisitionConfig(
        city="Kochi",
        state="Kerala",
        airport_iata=["COK"],
        portals_priority=["99acres", "magicbricks", "housing"],
        search_localities=[
            "Nedumbassery", "Angamaly", "Aluva", "Perumbavoor",
            "Manjapra", "Kalady",
        ],
        avg_price_buy_inr_per_sqft=7500,
        avg_rent_inr_per_sqft_per_month=22,
        market_trend="stable",
        investor_type="NRI",
        typical_deal_size_cr=2.0,
        land_record_authority="Kerala Land Records, GCDA/Kochi Metro",
        lpi_mandate_status="pending",
        stamp_duty_pct=8.0,
        registration_charges_pct=2.0,
        known_encroachment_risk="moderate",
        uig_zone_priority=9,
        target_property_types=["apartment", "villa", "commercial"],
        acquisition_goal="both",
        top_agent_firms=["Asset Homes", "Skyline Builders"],
        agent_commission_buy_pct=2.0,
        agent_commission_rent_pct=8.33,
        notes="World's first solar-powered airport. NRI diaspora investment hub. "
              "Cochin Smart City + Infopark IT cluster.",
    ),

    # ── GOA ───────────────────────────────────────────────────────────────────
    "Panaji": CityAcquisitionConfig(
        city="Panaji",
        state="Goa",
        airport_iata=["GOI", "GOX"],
        portals_priority=["magicbricks", "99acres", "housing"],
        search_localities=[
            "Vasco da Gama", "Chicalim", "Bogmalo", "Dabolim",
            "Bambolim", "Old Goa", "Panaji",
        ],
        avg_price_buy_inr_per_sqft=12000,
        avg_rent_inr_per_sqft_per_month=40,
        market_trend="rising",
        investor_type="NRI",
        typical_deal_size_cr=4.0,
        land_record_authority="Goa Land Records, DSLR",
        lpi_mandate_status="active",
        stamp_duty_pct=3.5,
        registration_charges_pct=1.0,
        known_encroachment_risk="high",
        uig_zone_priority=10,
        target_property_types=["villa", "farmhouse", "apartment"],
        acquisition_goal="both",
        top_agent_firms=["Coldwell Banker Goa", "CBRE Goa", "ERA Goa"],
        agent_commission_buy_pct=2.0,
        agent_commission_rent_pct=8.33,
        notes="New Mopa airport opens North Goa. Highest NRI + international demand. "
              "Portuguese heritage property premiums. Holiday rental yields >8%.",
    ),
}

# Default config for cities not yet configured
DEFAULT_CONFIG = CityAcquisitionConfig(
    city="Unknown",
    state="Unknown",
    airport_iata=[],
    portals_priority=["99acres", "magicbricks", "nobroker"],
    search_localities=[],
    avg_price_buy_inr_per_sqft=5000,
    avg_rent_inr_per_sqft_per_month=15,
    market_trend="stable",
    investor_type="retail",
    typical_deal_size_cr=1.5,
    land_record_authority="State Revenue Department",
    lpi_mandate_status="lobby",
    stamp_duty_pct=5.0,
    registration_charges_pct=1.0,
    known_encroachment_risk="moderate",
    uig_zone_priority=99,
    target_property_types=["apartment", "plot"],
    acquisition_goal="both",
    top_agent_firms=[],
    agent_commission_buy_pct=2.0,
    agent_commission_rent_pct=8.33,
)


def get_city_config(city: str) -> CityAcquisitionConfig:
    return CITY_CONFIGS.get(city, DEFAULT_CONFIG)
