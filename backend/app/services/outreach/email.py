"""SendGrid email integration."""
import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From
from app.config import settings

logger = logging.getLogger(__name__)

INTERNAL_TEAM_EMAIL = "team@uigllc.org"


class EmailService:
    def __init__(self):
        self._client = SendGridAPIClient(settings.sendgrid_api_key)
        self._from_email = settings.outreach_from_email
        self._from_name = settings.outreach_from_name

    def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> dict:
        """Send an email to an external recipient (property owner)."""
        try:
            message = Mail(
                from_email=From(self._from_email, self._from_name),
                to_emails=To(to_email, to_name),
                subject=subject,
                plain_text_content=body,
                html_content=html_body or body.replace("\n", "<br>"),
            )
            resp = self._client.send(message)
            message_id = resp.headers.get("X-Message-Id")
            logger.info(f"Email sent to {to_email}: {message_id}")
            return {"message_id": message_id, "status": resp.status_code}

        except Exception as exc:
            logger.error(f"Email send failed to {to_email}: {exc}")
            return {"message_id": None, "status": "failed", "error": str(exc)}

    def send_internal(self, subject: str, body: str) -> dict:
        """Send an internal notification to the UIG team."""
        return self.send(
            to_email=INTERNAL_TEAM_EMAIL,
            to_name="UIG Acquisition Team",
            subject=f"[UIG Pipeline] {subject}",
            body=body,
        )
