"""Admin settings router — manage API keys, secrets, and system configuration."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models.system_setting import SystemSetting
from app.models.admin_user import AdminUser
from app.routers.admin_auth import get_admin_user, require_admin

router = APIRouter(
    prefix="/api/admin/settings",
    tags=["Admin Settings"],
    dependencies=[Depends(get_admin_user)],
)

# Setting categories and their descriptions
SETTING_CATEGORIES = {
    "ai": "AI services (Anthropic, OpenAI, etc.)",
    "outreach": "Communication channels (Twilio, SendGrid)",
    "crm": "CRM integrations (HubSpot)",
    "storage": "File storage (Google Drive)",
    "scraping": "Web scraping (Apify)",
    "social": "Social media (Instagram, LinkedIn, etc.)",
    "payments": "Payment gateways (Stripe, Razorpay)",
    "general": "General system configuration",
}

# Known settings with metadata
KNOWN_SETTINGS = {
    "anthropic_api_key": {"category": "ai", "is_secret": True, "description": "Anthropic Claude API key"},
    "openai_api_key": {"category": "ai", "is_secret": True, "description": "OpenAI GPT API key (optional)"},
    "twilio_account_sid": {"category": "outreach", "is_secret": True, "description": "Twilio Account SID"},
    "twilio_auth_token": {"category": "outreach", "is_secret": True, "description": "Twilio Auth Token"},
    "twilio_whatsapp_from": {"category": "outreach", "is_secret": False, "description": "WhatsApp sender number"},
    "sendgrid_api_key": {"category": "outreach", "is_secret": True, "description": "SendGrid API key"},
    "hubspot_api_key": {"category": "crm", "is_secret": True, "description": "HubSpot private app key"},
    "hubspot_portal_id": {"category": "crm", "is_secret": False, "description": "HubSpot portal/account ID"},
    "google_service_account_json": {"category": "storage", "is_secret": True, "description": "Google service account JSON"},
    "google_drive_folder_id": {"category": "storage", "is_secret": False, "description": "Google Drive root folder ID"},
    "apify_api_token": {"category": "scraping", "is_secret": True, "description": "Apify API token"},
    "instagram_access_token": {"category": "social", "is_secret": True, "description": "Instagram Graph API token"},
    "linkedin_access_token": {"category": "social", "is_secret": True, "description": "LinkedIn API access token"},
    "stripe_secret_key": {"category": "payments", "is_secret": True, "description": "Stripe secret key"},
    "razorpay_key_id": {"category": "payments", "is_secret": True, "description": "Razorpay key ID"},
}


# --- Schemas ---

class SettingCreate(BaseModel):
    key: str
    value: str
    category: str = "general"
    is_secret: bool = False
    description: Optional[str] = None

class SettingUpdate(BaseModel):
    value: str

class SettingResponse(BaseModel):
    id: int
    key: str
    value: str  # Masked for secrets
    category: str
    is_secret: bool
    description: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]
    model_config = {"from_attributes": True}


def _mask_value(value: str, is_secret: bool) -> str:
    """Mask secret values showing only last 4 chars."""
    if not is_secret or len(value) <= 4:
        return value
    return "•" * (len(value) - 4) + value[-4:]


# --- Endpoints ---

@router.get("/categories")
def list_categories():
    """List available setting categories."""
    return SETTING_CATEGORIES


@router.get("/known")
def list_known_settings():
    """List all known/recommended settings and whether they're configured."""
    return KNOWN_SETTINGS


@router.get("", response_model=List[SettingResponse])
def list_settings(category: Optional[str] = None, db: Session = Depends(get_db)):
    """List all configured settings (secrets are masked)."""
    query = db.query(SystemSetting)
    if category:
        query = query.filter(SystemSetting.category == category)
    settings = query.order_by(SystemSetting.category, SystemSetting.key).all()

    result = []
    for s in settings:
        resp = SettingResponse.model_validate(s)
        resp.value = _mask_value(s.value, s.is_secret)
        result.append(resp)
    return result


@router.post("", response_model=SettingResponse, status_code=201)
def create_setting(
    setting_in: SettingCreate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create or update a setting."""
    existing = db.query(SystemSetting).filter(SystemSetting.key == setting_in.key).first()
    if existing:
        existing.value = setting_in.value
        existing.updated_by = admin.email
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        resp = SettingResponse.model_validate(existing)
        resp.value = _mask_value(existing.value, existing.is_secret)
        return resp

    # Auto-detect metadata from known settings
    meta = KNOWN_SETTINGS.get(setting_in.key, {})
    setting = SystemSetting(
        key=setting_in.key,
        value=setting_in.value,
        category=meta.get("category", setting_in.category),
        is_secret=meta.get("is_secret", setting_in.is_secret),
        description=meta.get("description", setting_in.description),
        updated_by=admin.email,
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    resp = SettingResponse.model_validate(setting)
    resp.value = _mask_value(setting.value, setting.is_secret)
    return resp


@router.put("/{key}", response_model=SettingResponse)
def update_setting(
    key: str,
    update: SettingUpdate,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a specific setting value."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.value = update.value
    setting.updated_by = admin.email
    setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)
    resp = SettingResponse.model_validate(setting)
    resp.value = _mask_value(setting.value, setting.is_secret)
    return resp


@router.delete("/{key}")
def delete_setting(
    key: str,
    admin: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a setting."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    db.delete(setting)
    db.commit()
    return {"message": f"Setting '{key}' deleted"}


@router.get("/status")
def settings_status(db: Session = Depends(get_db)):
    """Check which required integrations are configured vs missing."""
    configured_keys = {s.key for s in db.query(SystemSetting.key).all()}
    status = {}
    for key, meta in KNOWN_SETTINGS.items():
        status[key] = {
            "configured": key in configured_keys,
            "category": meta["category"],
            "description": meta["description"],
        }
    configured_count = sum(1 for v in status.values() if v["configured"])
    return {
        "total_known": len(KNOWN_SETTINGS),
        "configured": configured_count,
        "missing": len(KNOWN_SETTINGS) - configured_count,
        "details": status,
    }
