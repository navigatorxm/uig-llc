"""Twilio WhatsApp API integration."""
import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self._client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self._from_number = settings.twilio_whatsapp_from

    def send(self, to_number: str, message: str) -> dict:
        """
        Send a WhatsApp message via Twilio.
        to_number should be E.164 format (e.g. +919876543210).
        Returns dict with 'sid' and 'status'.
        """
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        try:
            msg = self._client.messages.create(
                body=message,
                from_=self._from_number,
                to=to_number,
            )
            logger.info(f"WhatsApp sent to {to_number}: SID={msg.sid}")
            return {"sid": msg.sid, "status": msg.status}

        except TwilioRestException as exc:
            logger.error(f"WhatsApp send failed to {to_number}: {exc}")
            return {"sid": None, "status": "failed", "error": str(exc)}

    def get_message_status(self, sid: str) -> Optional[str]:
        """Fetch delivery status for a message SID."""
        try:
            msg = self._client.messages(sid).fetch()
            return msg.status
        except TwilioRestException as exc:
            logger.error(f"WhatsApp status fetch failed: {exc}")
            return None
