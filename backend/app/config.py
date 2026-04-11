from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    environment: str = "development"
    secret_key: str  # No default — must be set in .env
    allowed_origins: str = "http://localhost:3000"

    # Admin credentials (single-admin internal tool)
    admin_email: str = "admin@uigllc.org"
    admin_password_hash: str  # bcrypt hash — generate with: python scripts/hash_password.py

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AI Providers
    vertex_ai_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    groq_api_key: str = ""
    cerebras_api_key: str = ""
    fireworks_ai_api_key: str = ""

    # Twilio WhatsApp
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # SendGrid
    sendgrid_api_key: str = ""
    outreach_from_email: str = "philip.george@uigllc.org"
    outreach_from_name: str = "Philip George"

    # HubSpot
    hubspot_api_key: str = ""
    hubspot_portal_id: str = ""

    # Google Drive
    google_service_account_json: str = ""
    google_drive_folder_id: str = ""

    # Apify
    apify_api_token: str = ""

    # Sender identity
    sender_name: str = "Philip George"
    sender_title: str = "Property Acquisition Manager, Head of Asia Pacific"
    sender_company: str = "United Investing Group LLC"
    sender_website: str = "https://www.uigllc.org"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
