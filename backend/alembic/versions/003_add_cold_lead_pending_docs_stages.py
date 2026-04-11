"""add cold_lead and pending_docs pipeline stages

Revision ID: 003
Revises: 002
Create Date: 2026-04-11

Adds two new holding stages for re-engagement campaigns:
- cold_lead: No response after 72h (5 follow-ups exhausted in 48h intensive chain)
- pending_docs: Responded but docs incomplete after 14 days (Chain 2 cutoff)
"""
from alembic import op
import sqlalchemy as sa


revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    PostgreSQL: ALTER TYPE to add new enum values.
    For SQLite (dev), this is a no-op since SQLAlchemy handles enum as VARCHAR.
    """
    # Add new enum values to the existing pipeline_stage enum type
    op.execute("ALTER TYPE pipelinestage ADD VALUE IF NOT EXISTS 'cold_lead'")
    op.execute("ALTER TYPE pipelinestage ADD VALUE IF NOT EXISTS 'pending_docs'")


def downgrade() -> None:
    """
    Note: PostgreSQL does not support removing enum values directly.
    This would require recreating the enum type, which is complex.
    For a downgrade, these values should simply not be used.
    """
    pass
