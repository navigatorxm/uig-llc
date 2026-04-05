"""Claude-powered lead scoring for UIG property acquisition."""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import anthropic
from app.config import settings

logger = logging.getLogger(__name__)

SCORING_PROMPT = """You are a property acquisition analyst for United Investing Group LLC (UIG),
a global conglomerate acquiring real estate in Delhi NCR, India.

Analyze the following lead data and produce a lead quality score from 0-100.

Lead Data:
{lead_data}

Score based on these weighted factors:
1. Contact Completeness (25 pts max):
   - Has phone: +10
   - Has email: +8
   - Has WhatsApp: +7

2. Listing Freshness (20 pts max):
   - Listed < 3 days ago: +20
   - Listed 3-7 days ago: +15
   - Listed 7-14 days ago: +10
   - Listed 14-30 days ago: +5
   - Older than 30 days: +0

3. Location Value (20 pts max):
   - prime_ncr tier: +20
   - upper_mid tier: +15
   - mid tier: +10
   - peripheral tier: +5
   - unknown: +0

4. Owner Responsiveness (20 pts max):
   - Responded within 24h: +20
   - Responded within 72h: +15
   - Responded but slow: +10
   - No response yet (new): +5
   - No response after follow-ups: +0

5. Document Readiness (15 pts max):
   - Has LPI cert: +5
   - Has sale deed: +4
   - Has encumbrance cert: +3
   - Has other docs: +3

Respond ONLY with valid JSON in this exact format:
{{
  "score": <float 0-100>,
  "breakdown": {{
    "contact_completeness": <float>,
    "listing_freshness": <float>,
    "location_value": <float>,
    "owner_responsiveness": <float>,
    "document_readiness": <float>
  }},
  "priority": "<high|medium|low>",
  "reasoning": "<2-3 sentence explanation>",
  "recommended_action": "<next step to take>"
}}"""


class LeadScorer:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def score(self, lead_data: dict) -> dict:
        """
        Score a lead using Claude.
        lead_data dict should contain all available lead/property info.
        Returns score dict with score, breakdown, priority, reasoning.
        """
        prompt = SCORING_PROMPT.format(lead_data=json.dumps(lead_data, indent=2, default=str))

        try:
            message = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            result_text = message.content[0].text.strip()

            # Parse JSON response
            result = json.loads(result_text)
            logger.info(f"Lead scored: {result.get('score')} ({result.get('priority')})")
            return result

        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse lead score JSON: {exc}")
            return self._fallback_score(lead_data)
        except Exception as exc:
            logger.error(f"Lead scoring API error: {exc}")
            return self._fallback_score(lead_data)

    def _fallback_score(self, lead_data: dict) -> dict:
        """Rule-based fallback scoring when AI is unavailable."""
        score = 0.0
        breakdown = {
            "contact_completeness": 0,
            "listing_freshness": 0,
            "location_value": 0,
            "owner_responsiveness": 5,
            "document_readiness": 0,
        }

        if lead_data.get("phone"):
            breakdown["contact_completeness"] += 10
        if lead_data.get("email"):
            breakdown["contact_completeness"] += 8
        if lead_data.get("whatsapp"):
            breakdown["contact_completeness"] += 7

        loc_tier = lead_data.get("location_tag", "unknown")
        tier_scores = {"prime_ncr": 20, "upper_mid": 15, "mid": 10, "peripheral": 5}
        breakdown["location_value"] = tier_scores.get(loc_tier, 0)

        score = sum(breakdown.values())
        return {
            "score": min(score, 100),
            "breakdown": breakdown,
            "priority": "high" if score >= 60 else ("medium" if score >= 35 else "low"),
            "reasoning": "Fallback rule-based scoring (AI unavailable).",
            "recommended_action": "Initiate contact via WhatsApp",
        }
