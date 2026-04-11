"""
Timing constants and schedule definitions for the three ICP3A/UIG communication chains.

Chain 1 — Initial outreach + 5 follow-ups (all within 48 hours, cold-lead cutoff at 72h)
Chain 2 — Document collection (triggered on qualified stage, pending-docs cutoff at 14 days)
Chain 3 — Verification SLA targets (5 business days, escalate to Philip at 7 days)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


# =============================================================================
# CHAIN 1 — INITIAL OUTREACH + FOLLOW-UPS
# All values are in minutes from T+0 (send_initial_outreach dispatch time).
# =============================================================================

CHAIN1_INITIAL: int = 0                   # T+0h  — fire immediately
CHAIN1_FU1: int = 8 * 60                  # T+8h
CHAIN1_FU2: int = 16 * 60                 # T+16h
CHAIN1_FU3: int = 24 * 60                 # T+24h
CHAIN1_FU4: int = 36 * 60                 # T+36h
CHAIN1_FU5: int = 48 * 60                 # T+48h  — final follow-up
CHAIN1_COLD_LEAD_CUTOFF: int = 72 * 60    # T+72h  — move to cold_lead if still no response


# =============================================================================
# CHAIN 2 — DOCUMENT COLLECTION
# All values are in minutes from T+0 (send_document_request dispatch time).
# =============================================================================

CHAIN2_DOC_REQUEST: int = 0               # T+0h   — immediate
CHAIN2_DOC_FU1: int = 48 * 60            # T+48h  — 2 days
CHAIN2_DOC_FU2: int = 120 * 60           # T+120h — 5 days
CHAIN2_DOC_FU3: int = 240 * 60           # T+240h — 10 days (final follow-up)
CHAIN2_PENDING_DOCS_CUTOFF: int = 336 * 60  # T+336h — 14 days → move to pending_docs


# =============================================================================
# CHAIN 3 — VERIFICATION
# Expressed in business days (not minutes) because SLA tracking is day-based.
# =============================================================================

CHAIN3_VERIFICATION_SLA_DAYS: int = 5    # Target turnaround in business days
CHAIN3_ESCALATION_DAYS: int = 7          # Escalate to Philip if no result by day 7


# =============================================================================
# CHAIN SCHEDULE DATACLASS
# =============================================================================

@dataclass
class ChainSchedule:
    """
    Describes one communication chain as an ordered sequence of steps.

    Each step is a dict with:
      - delay_minutes (int)  : minutes from T+0 of this chain to fire this step
      - template_key  (str)  : key into WHATSAPP_TEMPLATES / EMAIL_TEMPLATES
      - channel       (str)  : "whatsapp", "email", or "both"
    """
    name: str
    steps: List[Dict] = field(default_factory=list)


# =============================================================================
# CHAIN 1 SCHEDULE INSTANCE
# =============================================================================

CHAIN1_SCHEDULE: ChainSchedule = ChainSchedule(
    name="chain1_initial_outreach",
    steps=[
        {
            "delay_minutes": CHAIN1_INITIAL,
            "template_key": "initial_contact_whatsapp",
            "channel": "both",        # WhatsApp + email
        },
        {
            "delay_minutes": CHAIN1_FU1,
            "template_key": "follow_up_1_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN1_FU2,
            "template_key": "follow_up_2_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN1_FU3,
            "template_key": "follow_up_3_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN1_FU4,
            "template_key": "follow_up_4_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN1_FU5,
            "template_key": "follow_up_5_whatsapp",
            "channel": "whatsapp",
        },
    ],
)


# =============================================================================
# CHAIN 2 SCHEDULE INSTANCE
# =============================================================================

CHAIN2_SCHEDULE: ChainSchedule = ChainSchedule(
    name="chain2_document_collection",
    steps=[
        {
            "delay_minutes": CHAIN2_DOC_REQUEST,
            "template_key": "document_request_whatsapp",
            "channel": "both",        # WhatsApp + email
        },
        {
            "delay_minutes": CHAIN2_DOC_FU1,
            "template_key": "doc_follow_up_1_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN2_DOC_FU2,
            "template_key": "doc_follow_up_2_whatsapp",
            "channel": "whatsapp",
        },
        {
            "delay_minutes": CHAIN2_DOC_FU3,
            "template_key": "doc_follow_up_3_whatsapp",
            "channel": "whatsapp",
        },
    ],
)


# =============================================================================
# HELPER
# =============================================================================

_CHAIN_MAP: Dict[str, ChainSchedule] = {
    CHAIN1_SCHEDULE.name: CHAIN1_SCHEDULE,
    CHAIN2_SCHEDULE.name: CHAIN2_SCHEDULE,
}


def get_next_step_delay(chain_name: str, attempt_number: int) -> int:
    """
    Return the delay in minutes for the nth step (0-indexed) of a named chain.

    Args:
        chain_name:    One of the ChainSchedule.name values, e.g.
                       "chain1_initial_outreach" or "chain2_document_collection".
        attempt_number: Zero-based index into the chain's steps list.

    Returns:
        delay_minutes (int) for that step.

    Raises:
        KeyError:   if chain_name is not registered.
        IndexError: if attempt_number is out of range for that chain.
    """
    schedule = _CHAIN_MAP[chain_name]
    return schedule.steps[attempt_number]["delay_minutes"]
