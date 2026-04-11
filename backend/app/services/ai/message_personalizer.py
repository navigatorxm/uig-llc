"""AI-powered message personalization using the unified AI client.

Uses Vertex AI (Gemini) as primary, with Anthropic fallback.
"""
import logging
from app.services.ai.client import ai_client

logger = logging.getLogger(__name__)

PERSONALIZATION_SYSTEM = """You are Philip George, Property Acquisition Manager and Head of Asia Pacific
at United Investing Group LLC (UIG), a diversified global conglomerate.
You write professional, warm WhatsApp messages to property owners."""

PERSONALIZATION_PROMPT = """Write a personalized WhatsApp message to a property owner to express interest in acquiring their property.

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
        self._client = ai_client

    async def personalize_whatsapp_async(self, context: dict) -> str:
        """Generate a personalized WhatsApp outreach message (async)."""
        prompt = PERSONALIZATION_PROMPT.format(context=str(context))

        try:
            return await self._client.generate(
                prompt,
                system=PERSONALIZATION_SYSTEM,
                max_tokens=400,
                temperature=0.5,
            )
        except Exception as exc:
            logger.error(f"Message personalization failed: {exc}")
            from app.services.outreach.templates import render_template
            return render_template("initial_contact_whatsapp", context)

    def personalize_whatsapp(self, context: dict) -> str:
        """Sync wrapper for backward compatibility."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.personalize_whatsapp_async(context)).result()
            return loop.run_until_complete(self.personalize_whatsapp_async(context))
        except RuntimeError:
            return asyncio.run(self.personalize_whatsapp_async(context))
