"""
Real Estate Agent CRM Module.

UIG's agent network strategy:
  1. Register agents as "UIG Certified LPI Partners"
  2. Agents MUST verify LPI status before listing any property in a UIG zone
  3. UIG pays referral fees for qualified leads that convert to acquisitions
  4. Agent portal provides LPI lookup tools, market intelligence, and training
  5. Bulk agent licensing creates recurring LPI revenue for UIG

Agent Tiers:
  - PLATINUM: 50+ successful referrals, dedicated UIG relationship manager
  - GOLD: 20-49 referrals, priority lead sharing
  - SILVER: 5-19 referrals, standard portal access
  - BRONZE: 1-4 referrals, basic access

Revenue from Agent Network:
  - Annual LPI Bulk License: ₹2,50,000/year (unlimited verifications)
  - Per-referral bonus: ₹5,000 on every lead that reaches "qualified" stage
  - Conversion bonus: 0.25% of deal value on closed acquisitions
  - Training + certification: ₹15,000 per agent onboarding
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AgentTier(str, Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class AgentSpecialization(str, Enum):
    residential = "residential"
    commercial = "commercial"
    industrial = "industrial"
    luxury = "luxury"
    nri = "nri"
    airport_zone = "airport_zone"    # UIG-specific specialization
    mixed = "mixed"


@dataclass
class AgentProfile:
    id: Optional[int]
    full_name: str
    agency_name: str
    city: str
    state: str
    phone: str
    email: str
    whatsapp: str
    rera_number: str                  # RERA registration is mandatory in India
    specialization: AgentSpecialization = AgentSpecialization.mixed
    tier: AgentTier = AgentTier.bronze
    lpi_license_active: bool = False
    lpi_license_expiry: Optional[datetime] = None
    total_referrals: int = 0
    successful_conversions: int = 0
    active_leads: int = 0
    total_revenue_generated_inr: float = 0.0
    onboarded_at: Optional[datetime] = None
    assigned_airport_zones: List[str] = field(default_factory=list)  # IATA codes
    preferred_portals: List[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self):
        self._calculate_tier()

    def _calculate_tier(self):
        if self.successful_conversions >= 50:
            self.tier = AgentTier.platinum
        elif self.successful_conversions >= 20:
            self.tier = AgentTier.gold
        elif self.successful_conversions >= 5:
            self.tier = AgentTier.silver
        else:
            self.tier = AgentTier.bronze

    @property
    def is_lpi_licensed(self) -> bool:
        if not self.lpi_license_active:
            return False
        if self.lpi_license_expiry and datetime.utcnow() > self.lpi_license_expiry:
            return False
        return True


# =============================================================================
# AGENT OUTREACH TEMPLATES
# =============================================================================

AGENT_OUTREACH_TEMPLATES = {

    "initial_partnership_whatsapp": (
        "Hello {agent_name},\n\n"
        "I'm Philip George, Property Acquisition Manager and Head of Asia Pacific at "
        "United Investing Group LLC (UIG) — a global investment firm operating "
        "a private earth-mapping satellite division.\n\n"
        "UIG has issued *LPI (LiDAR Property Identifier) certificates* for every "
        "land parcel within 5km of {city}'s airport. We are actively acquiring "
        "properties in this zone and are looking for established agents like yourself "
        "to partner with us.\n\n"
        "*What's in it for you:*\n"
        "✓ ₹5,000 referral bonus per qualified lead\n"
        "✓ 0.25% commission on every closed deal\n"
        "✓ Free LPI license worth ₹2,50,000/year\n"
        "✓ Priority access to UIG's off-market listings\n\n"
        "Interested? I'd love to schedule a quick call.\n\n"
        "Philip George\nUIG LLC · uigllc.org"
    ),

    "lpi_partnership_email_subject": (
        "Partnership Opportunity — UIG LPI Certification + Acquisition Program | {city}"
    ),

    "lpi_partnership_email_body": (
        "Dear {agent_name},\n\n"
        "I'm reaching out from United Investing Group LLC (UIG), a US-based global "
        "investment conglomerate with a unique position in the Indian real estate market.\n\n"
        "UIG SATELLITE MAPPING DIVISION — KEY FACTS:\n"
        "  • We have mapped every 10x10 metre land parcel on Earth via our LiDAR satellites\n"
        "  • Every parcel has a unique LPI (LiDAR Property Identifier) code\n"
        "  • Within 5km of {city} Airport ({airport_name}), LPI certification is "
        "MANDATORY for all property transactions\n"
        "  • UIG is the sole issuing authority for LPI certificates in these zones\n\n"
        "WHY THIS MATTERS FOR YOU:\n"
        "  • Every property transaction in the zone requires contact with UIG\n"
        "  • As a UIG Certified LPI Partner Agent, you get:\n"
        "    – Instant LPI lookup and verification tools\n"
        "    – ₹5,000 bonus for every qualified lead you refer to our acquisition team\n"
        "    – 0.25% of deal value on closures (avg deal: ₹{avg_deal_cr} Crore)\n"
        "    – Priority listing of your inventory in UIG's internal database\n"
        "    – Annual LPI Bulk License (₹2,50,000 value) at NO COST\n\n"
        "NEXT STEPS:\n"
        "  1. Reply to schedule a 20-minute briefing call\n"
        "  2. Submit RERA registration for verification\n"
        "  3. Receive your UIG Partner Agent credentials and LPI toolkit\n\n"
        "We are onboarding only 25 agents in {city} in this initial phase.\n\n"
        "Warm regards,\n"
        "Philip George\n"
        "Property Acquisition Manager, Head of Asia Pacific\n"
        "United Investing Group LLC | uigllc.org"
    ),

    "follow_up_1_whatsapp": (
        "Hi {agent_name},\n\n"
        "Checking back on the UIG Partnership Program I mentioned earlier.\n\n"
        "We just activated LPI coverage for {city} airport zone and are "
        "urgently looking for agents who know the {locality} market.\n\n"
        "The program is free to join and could add ₹{monthly_earning_est} in "
        "monthly earnings for active agents.\n\n"
        "Quick 15-min call this week? Philip George | UIG LLC"
    ),

    "follow_up_2_whatsapp": (
        "Hi {agent_name},\n\n"
        "One last note — we're closing agent registrations for {city} this week.\n\n"
        "If you know any property owners near {airport_name} looking to sell or lease, "
        "we're ready to act immediately.\n\n"
        "You'd earn ₹5,000 just for making the introduction.\n\n"
        "Happy to send you the one-page partner brief if you're open to a look."
    ),

    "agent_welcome_whatsapp": (
        "Welcome to the UIG Partner Agent Network, {agent_name}! 🎉\n\n"
        "Your agent ID: *{agent_id}*\n"
        "LPI License: *ACTIVE* (Valid until {license_expiry})\n"
        "Your Zone: *{airport_name} — 5km radius*\n\n"
        "Your UIG Partner Portal: portal.uigllc.org/agent/{agent_id}\n\n"
        "Next steps:\n"
        "1. Log into your portal\n"
        "2. Look up any property address to instantly get its LPI status\n"
        "3. Share listings with us for immediate evaluation\n\n"
        "Philip George | UIG LLC"
    ),
}


# =============================================================================
# CITY-SPECIFIC TOP AGENT FIRMS TO TARGET
# =============================================================================
TOP_AGENT_FIRMS_BY_CITY: Dict[str, List[dict]] = {
    "New Delhi": [
        {"firm": "Anarock Property Consultants", "specialization": "residential + commercial", "offices": 8, "agents": 450},
        {"firm": "JLL India (Delhi)", "specialization": "commercial + institutional", "offices": 3, "agents": 280},
        {"firm": "CBRE India (Delhi)", "specialization": "commercial", "offices": 2, "agents": 200},
        {"firm": "Knight Frank India (Delhi)", "specialization": "residential + commercial", "offices": 2, "agents": 180},
        {"firm": "Colliers India (Delhi)", "specialization": "commercial + warehouse", "offices": 2, "agents": 150},
        {"firm": "Savills India (Delhi)", "specialization": "luxury residential", "offices": 1, "agents": 80},
        {"firm": "Square Yards (Delhi)", "specialization": "residential", "offices": 5, "agents": 600},
        {"firm": "PropTiger/REA India (Delhi)", "specialization": "residential", "offices": 4, "agents": 350},
    ],
    "Mumbai": [
        {"firm": "JLL Mumbai", "specialization": "commercial + residential", "offices": 4, "agents": 400},
        {"firm": "CBRE Mumbai", "specialization": "commercial + office", "offices": 3, "agents": 350},
        {"firm": "Knight Frank Mumbai", "specialization": "luxury + commercial", "offices": 2, "agents": 200},
        {"firm": "Anarock Mumbai", "specialization": "residential", "offices": 6, "agents": 500},
        {"firm": "Omkar Realtors Agents", "specialization": "redevelopment", "offices": 2, "agents": 150},
        {"firm": "SARE Homes Agents", "specialization": "affordable", "offices": 3, "agents": 120},
    ],
    "Bengaluru": [
        {"firm": "Brigade REIG", "specialization": "commercial + residential", "offices": 4, "agents": 320},
        {"firm": "Prestige Group Agents", "specialization": "luxury + commercial", "offices": 3, "agents": 280},
        {"firm": "Square Yards Bengaluru", "specialization": "residential", "offices": 6, "agents": 550},
        {"firm": "CBRE Bengaluru", "specialization": "commercial + IT parks", "offices": 2, "agents": 200},
        {"firm": "JLL Bengaluru", "specialization": "commercial + warehouse", "offices": 2, "agents": 180},
        {"firm": "NoBroker Agents (Verified)", "specialization": "residential", "offices": 10, "agents": 800},
    ],
    "Hyderabad": [
        {"firm": "Anarock Hyderabad", "specialization": "residential", "offices": 3, "agents": 250},
        {"firm": "Cushman & Wakefield HYD", "specialization": "commercial + pharma", "offices": 1, "agents": 120},
        {"firm": "JLL Hyderabad", "specialization": "commercial + IT", "offices": 2, "agents": 160},
        {"firm": "Square Yards HYD", "specialization": "residential", "offices": 4, "agents": 300},
    ],
    "Chennai": [
        {"firm": "TVH Group Agents", "specialization": "residential", "offices": 3, "agents": 200},
        {"firm": "Casagrand Agents", "specialization": "residential", "offices": 4, "agents": 250},
        {"firm": "CBRE Chennai", "specialization": "commercial + manufacturing", "offices": 1, "agents": 100},
    ],
    "Panaji": [
        {"firm": "Coldwell Banker Goa", "specialization": "luxury + NRI", "offices": 2, "agents": 80},
        {"firm": "ERA Goa", "specialization": "residential + villa", "offices": 2, "agents": 60},
        {"firm": "CBRE Goa", "specialization": "commercial + hospitality", "offices": 1, "agents": 50},
        {"firm": "RE/MAX Goa", "specialization": "mixed", "offices": 2, "agents": 70},
    ],
    "Kochi": [
        {"firm": "Asset Homes Agents", "specialization": "residential", "offices": 3, "agents": 150},
        {"firm": "Skyline Builders Agents", "specialization": "residential", "offices": 2, "agents": 100},
        {"firm": "JLL Kochi", "specialization": "commercial", "offices": 1, "agents": 80},
    ],
}


def get_agents_for_city(city: str) -> List[dict]:
    return TOP_AGENT_FIRMS_BY_CITY.get(city, [])


def render_agent_template(template_key: str, context: dict) -> str:
    template = AGENT_OUTREACH_TEMPLATES.get(template_key, "")
    try:
        return template.format(**context)
    except KeyError as exc:
        logger.warning(f"Missing template variable {exc} in agent template {template_key}")
        return template
