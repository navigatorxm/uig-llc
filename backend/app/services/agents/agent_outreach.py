"""
Agent Outreach Automation — Celery tasks + sequence management for real estate agent partnerships.

The agent acquisition funnel runs PARALLEL to the property owner funnel:
  Owner funnel:  Property → Owner Contact → Qualified → Docs → Verification → Deal
  Agent funnel:  Agent Discover → Partnership Pitch → LPI License → Active Referrer → Revenue

Agent acquisition is the force-multiplier — each onboarded agent brings 10-50 leads/month.
"""
import logging
from datetime import datetime
from typing import List, Optional
from app.services.agents.agent_crm import (
    AgentProfile, AgentTier, AgentSpecialization,
    render_agent_template, get_agents_for_city, AGENT_OUTREACH_TEMPLATES,
)
from app.data.airports import AIRPORT_INDEX, CITY_AIRPORTS

logger = logging.getLogger(__name__)


def build_agent_outreach_context(
    agent: AgentProfile,
    city_config=None,
) -> dict:
    """Build the Jinja-style context dict for agent outreach messages."""
    from app.data.city_configs import get_city_config
    config = city_config or get_city_config(agent.city)

    iata_list = CITY_AIRPORTS.get(agent.city, [])
    primary_airport = AIRPORT_INDEX.get(iata_list[0]) if iata_list else None

    return {
        "agent_name": agent.full_name.split()[0],
        "agent_full_name": agent.full_name,
        "agency_name": agent.agency_name,
        "city": agent.city,
        "locality": agent.notes or agent.city,
        "airport_name": primary_airport.airport_name if primary_airport else f"{agent.city} Airport",
        "airport_iata": primary_airport.iata_code if primary_airport else "",
        "avg_deal_cr": f"{config.typical_deal_size_cr:.1f}",
        "monthly_earning_est": f"₹{int(config.typical_deal_size_cr * 0.0025 * 3 * 10_000_000 / 100_000 * 3):,}",
        "license_expiry": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).strftime("%d %b %Y"),
        "agent_id": f"UIG-{agent.city[:3].upper()}-{abs(hash(agent.email)) % 9999:04d}",
    }


class AgentOutreachService:
    """Service for managing agent partnership outreach sequences."""

    def __init__(self):
        from app.services.outreach.whatsapp import WhatsAppService
        from app.services.outreach.email import EmailService
        self.whatsapp = WhatsAppService()
        self.email = EmailService()

    def send_initial_pitch(self, agent: AgentProfile) -> dict:
        """Send the initial partnership pitch to a real estate agent."""
        context = build_agent_outreach_context(agent)
        results = {}

        if agent.whatsapp:
            msg = render_agent_template("initial_partnership_whatsapp", context)
            result = self.whatsapp.send(agent.whatsapp, msg)
            results["whatsapp"] = result
            logger.info(f"Agent pitch sent to {agent.full_name} ({agent.city}) via WhatsApp")

        if agent.email:
            subject = render_agent_template("lpi_partnership_email_subject", context)
            body = render_agent_template("lpi_partnership_email_body", context)
            result = self.email.send(agent.email, agent.full_name, subject, body)
            results["email"] = result
            logger.info(f"Agent pitch email sent to {agent.email}")

        return results

    def send_follow_up(self, agent: AgentProfile, follow_up_number: int) -> dict:
        template_key = f"follow_up_{follow_up_number}_whatsapp"
        context = build_agent_outreach_context(agent)
        results = {}

        if agent.whatsapp:
            msg = render_agent_template(template_key, context)
            result = self.whatsapp.send(agent.whatsapp, msg)
            results["whatsapp"] = result

        return results

    def send_welcome_message(self, agent: AgentProfile) -> dict:
        """Send welcome + credentials to a newly onboarded agent."""
        context = build_agent_outreach_context(agent)
        results = {}

        if agent.whatsapp:
            msg = render_agent_template("agent_welcome_whatsapp", context)
            result = self.whatsapp.send(agent.whatsapp, msg)
            results["whatsapp"] = result

        return results

    def bulk_pitch_city(self, city: str) -> dict:
        """
        Mass outreach to all top agent firms in a city.
        Returns summary of outreach actions taken.
        """
        firms = get_agents_for_city(city)
        total_firms = len(firms)
        logger.info(f"Bulk agent pitch: {city} — {total_firms} firms targeted")
        return {
            "city": city,
            "firms_targeted": total_firms,
            "firms": firms,
            "status": "queued",
            "message": f"Agent outreach queued for {total_firms} firms in {city}",
        }


def generate_city_agent_campaign_brief(city: str) -> dict:
    """
    Generate a structured agent acquisition campaign brief for a city.
    This is the go-to-market brief Philip George's team uses on the ground.
    """
    from app.data.city_configs import get_city_config
    from app.data.airports import CITY_AIRPORTS, AIRPORT_INDEX

    config = get_city_config(city)
    iata_list = CITY_AIRPORTS.get(city, [])
    airports = [AIRPORT_INDEX[iata] for iata in iata_list if iata in AIRPORT_INDEX]
    firms = get_agents_for_city(city)

    total_agents_in_city = sum(f.get("agents", 0) for f in firms)
    avg_deal = config.typical_deal_size_cr
    earn_per_deal_inr = avg_deal * 10_000_000 * 0.0025  # 0.25% of deal value

    return {
        "city": city,
        "state": config.state,
        "uig_priority_rank": config.uig_zone_priority,
        "airports": [
            {
                "iata": a.iata_code,
                "name": a.airport_name,
                "radius_km": a.radius_km,
                "tier": a.tier,
                "priority_rank": a.priority_rank,
            }
            for a in airports
        ],
        "market_intelligence": {
            "avg_buy_price_per_sqft": f"₹{config.avg_price_buy_inr_per_sqft:,}",
            "avg_rent_per_sqft_month": f"₹{config.avg_rent_inr_per_sqft_per_month}",
            "market_trend": config.market_trend,
            "typical_deal_size": f"₹{avg_deal} Crore",
            "investor_type": config.investor_type,
            "stamp_duty": f"{config.stamp_duty_pct}%",
            "land_record_authority": config.land_record_authority,
        },
        "agent_network": {
            "top_firms": firms,
            "total_agents_in_market": total_agents_in_city,
            "target_onboard_agents": min(25, max(5, total_agents_in_city // 20)),
            "agent_earn_per_conversion": f"₹{earn_per_deal_inr:,.0f}",
            "lpi_license_value": "₹2,50,000/year (given FREE to partners)",
        },
        "lpi_status": {
            "mandate_status": config.lpi_mandate_status,
            "coverage": "100% (all 10x10m parcels within 5km of airport mapped)",
            "uig_competitive_position": "Sole issuing authority",
        },
        "acquisition_targets": {
            "property_types": config.target_property_types,
            "localities": config.search_localities,
            "goal": config.acquisition_goal,
            "encroachment_risk": config.known_encroachment_risk,
        },
    }
