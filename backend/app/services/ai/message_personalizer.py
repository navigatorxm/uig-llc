"""AI-powered message personalization using Claude."""
import logging
import anthropic
from app.config import settings

logger = logging.getLogger(__name__)

PERSONALIZATION_PROMPT = """You are Philip George, Property Acquisition Manager and Head of Asia Pacific
at United Investing Group LLC (UIG), a diversified global conglomerate.

Write a personalized WhatsApp message to a property owner to express interest in acquiring their property.

Property/Owner Details:
{context}

Guidelines:
- Be professional yet warm and approachable
- Keep it under 200 words
- Mention UIG's credibility briefly
- Ask for their expectations (price, conditions, timeline)
- Do not use markdown formatting — plain text only
- End with the signature:

Warm regards,
Philip George
Property Acquisition Manager, Head of Asia Pacific
United Investing Group LLC
www.uigllc.org

Write only the message body, nothing else."""


class MessagePersonalizer:
    def __init__(self):
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def personalize_whatsapp(self, context: dict) -> str:
        """Generate a personalized WhatsApp outreach message."""
        prompt = PERSONALIZATION_PROMPT.format(context=str(context))

        try:
            message = self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()

        except Exception as exc:
            logger.error(f"Message personalization failed: {exc}")
            # Fall back to standard template
            from app.services.outreach.templates import render_template
            return render_template("initial_contact_whatsapp", context)
