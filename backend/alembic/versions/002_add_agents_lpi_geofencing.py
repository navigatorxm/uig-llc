"""Add agents, LPI certificates, and geofencing columns

Revision ID: 002
Revises: 001
Create Date: 2026-03-30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── agents ────────────────────────────────────────────────────────────────
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("agency_name", sa.String(255)),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100)),
        sa.Column("phone", sa.String(20), unique=True),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("whatsapp", sa.String(20)),
        sa.Column("rera_number", sa.String(50), unique=True),
        sa.Column("specialization", sa.String(50), server_default="mixed"),
        sa.Column("tier", sa.String(20), server_default="bronze"),
        sa.Column("status", sa.String(30), server_default="prospect"),
        sa.Column("lpi_license_active", sa.Boolean, server_default="false"),
        sa.Column("lpi_license_issued_at", sa.DateTime),
        sa.Column("lpi_license_expiry", sa.DateTime),
        sa.Column("lpi_verifications_count", sa.Integer, server_default="0"),
        sa.Column("total_referrals", sa.Integer, server_default="0"),
        sa.Column("successful_conversions", sa.Integer, server_default="0"),
        sa.Column("active_leads_count", sa.Integer, server_default="0"),
        sa.Column("total_revenue_generated_inr", sa.Float, server_default="0"),
        sa.Column("total_fees_paid_inr", sa.Float, server_default="0"),
        sa.Column("assigned_airport_zones", sa.JSON, server_default="[]"),
        sa.Column("preferred_portals", sa.JSON, server_default="[]"),
        sa.Column("first_contact_at", sa.DateTime),
        sa.Column("last_contact_at", sa.DateTime),
        sa.Column("contact_attempts", sa.Integer, server_default="0"),
        sa.Column("responded", sa.Boolean, server_default="false"),
        sa.Column("hubspot_contact_id", sa.String(100)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_agents_city", "agents", ["city"])
    op.create_index("ix_agents_status", "agents", ["status"])

    # ── lpi_certificates ──────────────────────────────────────────────────────
    op.create_table(
        "lpi_certificates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("certificate_id", sa.String(100), unique=True, nullable=False),
        sa.Column("lpi_codes", sa.JSON, nullable=False),
        sa.Column("property_address", sa.Text, nullable=False),
        sa.Column("owner_name", sa.String(255)),
        sa.Column("city", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("total_area_sqm", sa.Float),
        sa.Column("in_airport_zone", sa.Boolean, server_default="false"),
        sa.Column("nearest_airport_iata", sa.String(10)),
        sa.Column("airport_distance_km", sa.Float),
        sa.Column("zone_priority", sa.String(20)),
        sa.Column("status", sa.String(20), server_default="valid"),
        sa.Column("issued_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("valid_until", sa.DateTime),
        sa.Column("flags", sa.JSON, server_default="[]"),
        sa.Column("satellite_id", sa.String(50), server_default="UIG-SAT-3"),
        sa.Column("scan_resolution_cm", sa.Float, server_default="10"),
        sa.Column("lidar_scan_date", sa.DateTime),
        sa.Column("encroachment_detected", sa.Boolean, server_default="false"),
        sa.Column("flood_risk_score", sa.Float, server_default="0"),
        sa.Column("seismic_zone", sa.String(5)),
        sa.Column("issuance_fee_inr", sa.Float, server_default="15000"),
        sa.Column("fee_paid", sa.Boolean, server_default="false"),
        sa.Column("fee_paid_at", sa.DateTime),
        sa.Column("lead_id", sa.Integer, sa.ForeignKey("leads.id")),
        sa.Column("issued_by_agent_id", sa.Integer, sa.ForeignKey("agents.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_lpi_city", "lpi_certificates", ["city"])
    op.create_index("ix_lpi_in_airport_zone", "lpi_certificates", ["in_airport_zone"])
    op.create_index("ix_lpi_certificate_id", "lpi_certificates", ["certificate_id"])

    # ── Add geofencing columns to properties ──────────────────────────────────
    op.add_column("properties", sa.Column("in_airport_zone", sa.Boolean, server_default="false"))
    op.add_column("properties", sa.Column("nearest_airport_iata", sa.String(10)))
    op.add_column("properties", sa.Column("airport_distance_km", sa.Float))
    op.add_column("properties", sa.Column("zone_priority", sa.String(20)))
    op.add_column("properties", sa.Column("requires_lpi", sa.Boolean, server_default="false"))
    op.add_column("properties", sa.Column("lpi_certificate_id", sa.String(100)))


def downgrade() -> None:
    for col in ["in_airport_zone", "nearest_airport_iata", "airport_distance_km",
                "zone_priority", "requires_lpi", "lpi_certificate_id"]:
        op.drop_column("properties", col)
    op.drop_table("lpi_certificates")
    op.drop_table("agents")
