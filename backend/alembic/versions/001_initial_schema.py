"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- leads ---
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("owner_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(255)),
        sa.Column("whatsapp", sa.String(20)),
        sa.Column("pipeline_stage", sa.String(50), nullable=False, server_default="new_lead"),
        sa.Column("lead_score", sa.Float, server_default="0"),
        sa.Column("lead_score_breakdown", sa.Text),
        sa.Column("hubspot_contact_id", sa.String(100), unique=True),
        sa.Column("first_contact_at", sa.DateTime),
        sa.Column("last_contact_at", sa.DateTime),
        sa.Column("contact_attempt_count", sa.Integer, server_default="0"),
        sa.Column("response_received", sa.Boolean, server_default="false"),
        sa.Column("interested", sa.Boolean),
        sa.Column("notes", sa.Text),
        sa.Column("assigned_to", sa.String(255)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_leads_phone", "leads", ["phone"])
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_pipeline_stage", "leads", ["pipeline_stage"])

    # --- properties ---
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_portal", sa.String(50), nullable=False),
        sa.Column("listing_url", sa.Text, unique=True),
        sa.Column("title", sa.String(500)),
        sa.Column("property_type", sa.String(50)),
        sa.Column("transaction_type", sa.String(10), nullable=False),
        sa.Column("price", sa.Float),
        sa.Column("price_currency", sa.String(10), server_default="INR"),
        sa.Column("area_sqft", sa.Float),
        sa.Column("address", sa.Text),
        sa.Column("locality", sa.String(255)),
        sa.Column("city", sa.String(100), server_default="Delhi"),
        sa.Column("pincode", sa.String(10)),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("owner_name", sa.String(255)),
        sa.Column("owner_phone", sa.String(20)),
        sa.Column("owner_email", sa.String(255)),
        sa.Column("owner_whatsapp", sa.String(20)),
        sa.Column("listing_date", sa.DateTime),
        sa.Column("scraped_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("is_duplicate", sa.Boolean, server_default="false"),
        sa.Column("budget_range", sa.String(50)),
        sa.Column("location_tag", sa.String(100)),
        sa.Column("lead_id", sa.Integer, sa.ForeignKey("leads.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # --- documents ---
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lead_id", sa.Integer, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False),
        sa.Column("google_drive_file_id", sa.String(255)),
        sa.Column("google_drive_url", sa.Text),
        sa.Column("original_filename", sa.String(500)),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("verified", sa.Boolean, server_default="false"),
        sa.Column("verified_at", sa.DateTime),
        sa.Column("verified_by", sa.String(255)),
        sa.Column("rejection_reason", sa.Text),
        sa.Column("ai_analysis", sa.Text),
        sa.Column("ai_flags", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # --- deals ---
    op.create_table(
        "deals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lead_id", sa.Integer, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("property_id", sa.Integer, sa.ForeignKey("properties.id")),
        sa.Column("deal_type", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("agreed_price", sa.Float),
        sa.Column("price_currency", sa.String(10), server_default="INR"),
        sa.Column("hubspot_deal_id", sa.String(100), unique=True),
        sa.Column("site_visit_scheduled_at", sa.DateTime),
        sa.Column("agreement_signed_at", sa.DateTime),
        sa.Column("payment_completed_at", sa.DateTime),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # --- outreach_logs ---
    op.create_table(
        "outreach_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lead_id", sa.Integer, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("message_template", sa.String(100)),
        sa.Column("message_body", sa.Text),
        sa.Column("sent_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("delivered", sa.Boolean),
        sa.Column("delivery_sid", sa.String(255)),
        sa.Column("response_text", sa.Text),
        sa.Column("response_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("outreach_logs")
    op.drop_table("deals")
    op.drop_table("documents")
    op.drop_table("properties")
    op.drop_table("leads")
