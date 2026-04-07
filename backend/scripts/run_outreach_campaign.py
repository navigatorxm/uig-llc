#!/usr/bin/env python3
"""
UIG Outreach Campaign Runner
============================
Queries all leads at 'new_lead' stage, AI-scores them, and fires the
WhatsApp + email initial outreach sequence via Celery.

The script handles:
  1. Load all new/uncontacted leads from the DB
  2. Score each lead with Claude AI (if not already scored)
  3. Filter by minimum score threshold
  4. Send WhatsApp + email outreach for each (via Celery or direct)
  5. Advance lead stage to 'contact_initiated'
  6. Log everything to outreach_logs table
  7. Print campaign report

Usage:
    python scripts/run_outreach_campaign.py
    python scripts/run_outreach_campaign.py --min-score 50 --limit 100
    python scripts/run_outreach_campaign.py --channel whatsapp
    python scripts/run_outreach_campaign.py --city "Delhi NCR" --channel both
    python scripts/run_outreach_campaign.py --dry-run --limit 20
    python scripts/run_outreach_campaign.py --stage new_lead qualified

Options:
    --min-score   Minimum lead score to include (default: 40)
    --limit       Max leads to process per run (default: 200)
    --channel     whatsapp | email | both (default: both)
    --city        Filter by city name
    --stage       Pipeline stages to include (default: new_lead)
    --dry-run     Show which leads would be contacted, no sends
    --no-score    Skip AI scoring pass (use raw score or 50 default)
    --delay       Seconds between sends (default: 2)
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("outreach_campaign")


# ── lead loading ──────────────────────────────────────────────────────────────

def load_leads(
    stages: List[str],
    city: Optional[str],
    limit: int,
):
    from app.database import SessionLocal
    from app.models.lead import Lead, PipelineStage
    from app.models.property import Property

    session = SessionLocal()
    try:
        stage_enums = []
        for s in stages:
            try:
                stage_enums.append(PipelineStage(s))
            except ValueError:
                log.warning(f"Unknown stage: {s}")

        query = session.query(Lead).filter(Lead.pipeline_stage.in_(stage_enums))

        if city:
            # Join property table to filter by city
            query = (
                query
                .join(Property, Property.lead_id == Lead.id)
                .filter(Property.city.ilike(f"%{city}%"))
            )

        query = query.order_by(Lead.lead_score.desc().nullslast(), Lead.created_at.asc())
        leads = query.limit(limit).all()
        return leads, session
    except Exception:
        session.close()
        raise


# ── AI scoring pass ───────────────────────────────────────────────────────────

def score_leads_batch(leads, session):
    """Score all unscored leads with Claude. Updates in-place."""
    unscored = [l for l in leads if l.lead_score is None]
    if not unscored:
        return

    try:
        from app.services.ai.lead_scorer import LeadScorer
        scorer = LeadScorer()
        log.info(f"Scoring {len(unscored)} unscored leads with Claude AI...")
        scored_count = 0
        for lead in unscored:
            try:
                result = scorer.score_lead(lead)
                lead.lead_score = result.score
                scored_count += 1
            except Exception as exc:
                log.warning(f"Scoring failed for lead {lead.id}: {exc}")
                lead.lead_score = 40  # default mid-score

        session.commit()
        log.info(f"Scoring complete: {scored_count}/{len(unscored)} leads scored")
    except ImportError:
        log.warning("Lead scorer unavailable — assigning default score 40")
        for lead in unscored:
            lead.lead_score = 40
        session.commit()


# ── outreach send ─────────────────────────────────────────────────────────────

def get_lead_property(lead, session):
    from app.models.property import Property
    return session.query(Property).filter(Property.lead_id == lead.id).first()


def build_whatsapp_context(lead, prop) -> Dict[str, Any]:
    return {
        "owner_name": lead.owner_name or "Sir/Madam",
        "property_address": (
            getattr(prop, "location", "") or
            getattr(prop, "locality", "") or
            "your property"
        ),
        "city": getattr(prop, "city", "") or "your city",
        "transaction_type": getattr(prop, "transaction_type", "buy"),
        "price": (
            f"₹{getattr(prop, 'price', 0) / 1e7:.1f} Cr"
            if getattr(prop, "price", None)
            else "the listed price"
        ),
    }


def send_whatsapp(lead, prop, session, dry_run: bool = False) -> bool:
    from app.services.outreach.templates import render_template
    from app.models.outreach_log import OutreachLog, OutreachChannel

    phone = lead.whatsapp or lead.phone
    if not phone:
        log.warning(f"  Lead {lead.id}: no phone/WhatsApp — skip")
        return False

    ctx = build_whatsapp_context(lead, prop)
    message = render_template("initial_contact_whatsapp", ctx)

    if dry_run:
        log.info(f"  [DRY-RUN] WhatsApp → +91{phone}: {message[:80]}...")
        return True

    try:
        from app.services.outreach.whatsapp import WhatsAppService
        svc = WhatsAppService()
        svc.send_message(to=f"+91{phone}", body=message)

        log_entry = OutreachLog(
            lead_id=lead.id,
            channel=OutreachChannel.whatsapp,
            message_template="initial_contact_whatsapp",
            sent_at=datetime.utcnow(),
            delivered=True,
        )
        session.add(log_entry)
        return True
    except Exception as exc:
        log.error(f"  WhatsApp failed for lead {lead.id}: {exc}")
        return False


def send_email(lead, prop, session, dry_run: bool = False) -> bool:
    from app.services.outreach.templates import render_template
    from app.models.outreach_log import OutreachLog, OutreachChannel

    if not lead.email:
        log.debug(f"  Lead {lead.id}: no email — skip")
        return False

    ctx = build_whatsapp_context(lead, prop)
    subject = render_template("initial_contact_email_subject", ctx)
    body = render_template("initial_contact_email_body", ctx)

    if dry_run:
        log.info(f"  [DRY-RUN] Email → {lead.email}: {subject}")
        return True

    try:
        from app.services.outreach.email import EmailService
        svc = EmailService()
        svc.send(to=lead.email, to_name=lead.owner_name, subject=subject, html_body=body)

        log_entry = OutreachLog(
            lead_id=lead.id,
            channel=OutreachChannel.email,
            message_template="initial_contact_email",
            sent_at=datetime.utcnow(),
            delivered=True,
        )
        session.add(log_entry)
        return True
    except Exception as exc:
        log.error(f"  Email failed for lead {lead.id}: {exc}")
        return False


# ── stage advance ─────────────────────────────────────────────────────────────

def advance_to_contact_initiated(lead, session):
    from app.models.lead import PipelineStage
    if lead.pipeline_stage == PipelineStage.new_lead:
        lead.pipeline_stage = PipelineStage.contact_initiated
        lead.first_contact_at = lead.first_contact_at or datetime.utcnow()
        lead.last_contact_at = datetime.utcnow()
        lead.contact_attempt_count = (lead.contact_attempt_count or 0) + 1
        lead.updated_at = datetime.utcnow()


# ── schedule follow-ups ───────────────────────────────────────────────────────

def schedule_follow_ups(lead_ids: List[int]):
    """Queue Celery follow-up tasks (Day 3 and Day 7) for contacted leads."""
    try:
        from app.workers.outreach_tasks import send_follow_up

        for lead_id in lead_ids:
            # Day 3 follow-up
            send_follow_up.apply_async(
                kwargs={"lead_id": lead_id, "follow_up_number": 1},
                countdown=3 * 24 * 3600,
            )
            # Day 7 follow-up
            send_follow_up.apply_async(
                kwargs={"lead_id": lead_id, "follow_up_number": 2},
                countdown=7 * 24 * 3600,
            )

        log.info(f"Scheduled follow-ups for {len(lead_ids)} leads (Day 3 + Day 7)")
    except ImportError:
        log.warning("Celery not available — follow-ups not scheduled")


# ── HubSpot sync ──────────────────────────────────────────────────────────────

def sync_to_hubspot(leads, session, dry_run: bool):
    if dry_run:
        return
    try:
        from app.services.crm.hubspot import HubSpotService
        hs = HubSpotService()
        synced = 0
        for lead in leads:
            try:
                contact_id = hs.create_or_update_contact(
                    email=lead.email or "",
                    name=lead.owner_name or "",
                    phone=lead.phone or "",
                    properties={
                        "pipeline_stage": str(lead.pipeline_stage.value),
                        "lead_score": str(lead.lead_score or 0),
                    },
                )
                if contact_id and not lead.hubspot_contact_id:
                    lead.hubspot_contact_id = contact_id
                    synced += 1
            except Exception:
                pass
        session.commit()
        log.info(f"HubSpot sync: {synced} contacts created/updated")
    except Exception as exc:
        log.warning(f"HubSpot sync failed: {exc}")


# ── reporting ─────────────────────────────────────────────────────────────────

def print_campaign_report(stats: Dict[str, Any], leads_processed: List[Any]):
    score_buckets = {"90-100": 0, "70-89": 0, "50-69": 0, "40-49": 0, "<40": 0}
    for lead in leads_processed:
        score = lead.lead_score or 0
        if score >= 90:
            score_buckets["90-100"] += 1
        elif score >= 70:
            score_buckets["70-89"] += 1
        elif score >= 50:
            score_buckets["50-69"] += 1
        elif score >= 40:
            score_buckets["40-49"] += 1
        else:
            score_buckets["<40"] += 1

    print("\n" + "=" * 60)
    print("  UIG OUTREACH CAMPAIGN REPORT")
    print("=" * 60)
    print(f"  Leads evaluated        : {stats['evaluated']}")
    print(f"  Filtered (below score) : {stats['filtered_below_score']}")
    print(f"  Leads contacted        : {stats['contacted']}")
    print(f"  WhatsApp sent          : {stats['whatsapp_sent']}")
    print(f"  Emails sent            : {stats['email_sent']}")
    print(f"  Both channels          : {stats['both_sent']}")
    print(f"  Failures               : {stats['failures']}")
    print(f"  HubSpot synced         : {stats.get('hubspot_synced', 0)}")

    print("\n  Lead score distribution:")
    for bucket, count in score_buckets.items():
        bar = "█" * min(count, 40)
        print(f"    {bucket:>8}  {bar:<40} {count}")

    print(f"\n  Follow-ups scheduled   : Day 3 + Day 7 for all contacted leads")
    print(f"  Campaign time          : {stats.get('elapsed_s', 0):.1f}s")
    print("=" * 60 + "\n")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UIG Outreach Campaign — contact all new leads via WhatsApp + email"
    )
    parser.add_argument("--min-score", type=int, default=40, help="Minimum AI score (0-100)")
    parser.add_argument("--limit", type=int, default=200, help="Max leads to contact per run")
    parser.add_argument(
        "--channel",
        choices=["whatsapp", "email", "both"],
        default="both",
        help="Outreach channel",
    )
    parser.add_argument("--city", type=str, default=None, help="Filter leads by city")
    parser.add_argument(
        "--stage",
        nargs="+",
        default=["new_lead"],
        help="Pipeline stages to process (default: new_lead)",
    )
    parser.add_argument("--dry-run", action="store_true", help="No sends — preview only")
    parser.add_argument("--no-score", action="store_true", help="Skip AI scoring pass")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between sends")
    args = parser.parse_args()

    started_at = datetime.utcnow()
    stats: Dict[str, Any] = {
        "evaluated": 0,
        "filtered_below_score": 0,
        "contacted": 0,
        "whatsapp_sent": 0,
        "email_sent": 0,
        "both_sent": 0,
        "failures": 0,
        "hubspot_synced": 0,
    }

    log.info(
        f"Campaign start | stages={args.stage} | "
        f"min_score={args.min_score} | limit={args.limit} | "
        f"channel={args.channel} | dry_run={args.dry_run}"
    )

    leads, session = load_leads(
        stages=args.stage,
        city=args.city,
        limit=args.limit * 3,  # load extra to account for filtering
    )
    stats["evaluated"] = len(leads)
    log.info(f"Loaded {len(leads)} leads from DB")

    if not args.no_score:
        score_leads_batch(leads, session)

    # filter by score
    qualified_leads = [l for l in leads if (l.lead_score or 0) >= args.min_score]
    stats["filtered_below_score"] = len(leads) - len(qualified_leads)
    qualified_leads = qualified_leads[: args.limit]

    log.info(
        f"After score filter (≥{args.min_score}): {len(qualified_leads)} leads to contact"
    )

    if not qualified_leads:
        log.warning("No leads qualify. Try lowering --min-score or importing more leads.")
        session.close()
        return

    contacted_ids = []

    for i, lead in enumerate(qualified_leads, start=1):
        prop = get_lead_property(lead, session)
        score = lead.lead_score or 0
        addr = getattr(prop, "location", "") or getattr(prop, "locality", "") or "N/A"
        log.info(
            f"[{i}/{len(qualified_leads)}] Lead {lead.id} | "
            f"{lead.owner_name} | score={score} | {addr}"
        )

        wa_ok = False
        email_ok = False

        if args.channel in ("whatsapp", "both"):
            wa_ok = send_whatsapp(lead, prop, session, dry_run=args.dry_run)
            if wa_ok:
                stats["whatsapp_sent"] += 1

        if args.channel in ("email", "both"):
            email_ok = send_email(lead, prop, session, dry_run=args.dry_run)
            if email_ok:
                stats["email_sent"] += 1

        if wa_ok or email_ok:
            stats["contacted"] += 1
            if wa_ok and email_ok:
                stats["both_sent"] += 1
            if not args.dry_run:
                advance_to_contact_initiated(lead, session)
                contacted_ids.append(lead.id)
        else:
            stats["failures"] += 1

        if not args.dry_run:
            try:
                session.commit()
            except Exception as exc:
                log.error(f"Commit failed for lead {lead.id}: {exc}")
                session.rollback()

        if args.delay > 0:
            time.sleep(args.delay)

    # Schedule follow-ups
    if contacted_ids and not args.dry_run:
        schedule_follow_ups(contacted_ids)

    # HubSpot sync
    sync_to_hubspot(qualified_leads, session, dry_run=args.dry_run)
    session.close()

    elapsed = (datetime.utcnow() - started_at).total_seconds()
    stats["elapsed_s"] = elapsed

    print_campaign_report(stats, qualified_leads)

    log.info(
        f"Campaign complete. {stats['contacted']} leads contacted "
        f"in {elapsed:.1f}s."
    )


if __name__ == "__main__":
    main()
