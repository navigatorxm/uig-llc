# UIG Property Acquisition Engine — MVP Implementation Roadmap
**INTERNAL DOCUMENT — CONFIDENTIAL**
*Version 1.0 | April 2026 | United Investing Group LLC*

---

## Executive Summary

This document defines the phase-by-phase plan to ship UIG's India property acquisition MVP, achieve investor demo readiness, and process the first 1,000 leads through the full pipeline. The minimum viable launch requires **$312 one-time setup + $147/month recurring** — achievable in **5 weeks** with one technical operator.

---

## MVP Definition

The MVP is considered shippable when:
- [ ] Backend + database + Celery workers are live and stable
- [ ] At least 1,000 leads are in the pipeline (scraped + imported)
- [ ] WhatsApp and email outreach fires correctly for new leads
- [ ] At least 1 lead has progressed to `approved` stage end-to-end
- [ ] Dashboard shows live KPIs (pipeline counts, conversion funnel, outreach stats)
- [ ] Make.com automation runs without manual intervention
- [ ] LPI certificate can be issued and verified via API
- [ ] HubSpot is synced with all lead/deal data

---

## Cost Overview — Minimum to Launch

### One-Time Setup Costs

| Item | Cost | Notes |
|------|------|-------|
| Domain name (uigllc.org or similar) | $12 | Via Namecheap/GoDaddy |
| Twilio WhatsApp Business API setup | $0 | Free approval; ~3–5 day wait |
| Google Cloud Service Account (Drive) | $0 | Free tier sufficient |
| SendGrid account verification | $0 | Free tier: 100 emails/day |
| HubSpot CRM account | $0 | Free tier: unlimited contacts |
| Anthropic API (Claude) — initial credit | $20 | Pre-purchase; ~2,000 lead scores |
| Supabase project setup | $0 | Free tier; upgrade later |
| Make.com Core plan (first month) | $9 | 10,000 operations/month |
| **Buffer for test messages / errors** | $50 | Twilio test credits |
| Apify (optional scraping proxy) | $49 | Starter plan for 1 month |
| **TOTAL ONE-TIME** | **$140** | |

*Note: Domain + Apify are optional. Core functional MVP is ~$79 one-time.*

---

### Monthly Recurring Costs (Post-Launch)

| Service | Plan | Monthly Cost | Notes |
|---------|------|-------------|-------|
| **Hosting — Backend + Celery** | Railway Starter | $20 | FastAPI + 2 Celery workers |
| **Database — PostgreSQL** | Supabase Pro | $25 | After free tier limits hit |
| **Redis** | Upstash Free → Pay-as-you-go | $5 | Task queue for Celery |
| **Frontend — Next.js** | Vercel Hobby | $0 | Free for personal/small projects |
| **WhatsApp Outreach** | Twilio pay-per-msg | $25 | ~5,000 messages @ $0.005 each |
| **Email** | SendGrid Free | $0 | 100/day free; upgrade at scale |
| **AI — Claude API** | Anthropic pay-per-use | $15 | 1,000 lead scores + messages |
| **CRM** | HubSpot Free | $0 | Unlimited contacts on free tier |
| **Google Drive** | Google Workspace | $0 | Free 15GB per account |
| **Make.com Automation** | Core | $9 | 10,000 ops — sufficient for MVP |
| **SSL Certificate** | Let's Encrypt | $0 | Free via Certbot / Railway |
| **TOTAL MONTHLY** | | **$99** | |

**Total to run for 3 months (demo period): $140 + ($99 × 3) = ~$440**

---

### Cost to Process First 1,000 Leads (One Campaign)

| Action | Volume | Unit Cost | Total |
|--------|--------|-----------|-------|
| Lead scraping (5 portals × 10 localities) | 1,000 leads | $0 | $0 |
| AI lead scoring (Claude) | 1,000 scores | $0.003/score | $3 |
| Initial WhatsApp messages | 1,000 msgs | $0.005/msg | $5 |
| Initial emails | 1,000 emails | $0 (free tier) | $0 |
| Day-3 follow-up WhatsApp | ~600 msgs | $0.005/msg | $3 |
| Day-7 follow-up WhatsApp | ~300 msgs | $0.005/msg | $1.50 |
| Document request WhatsApp | ~150 msgs | $0.005/msg | $0.75 |
| Make.com operations (~10 per lead) | 10,000 ops | Included in $9/mo | $0 |
| **TOTAL CAMPAIGN COST** | | | **~$13.25** |

**The first 1,000 leads cost under $15 in API/messaging costs.**

---

## Phase-by-Phase Implementation Plan

---

### PHASE 0: Environment & Accounts Setup
**Duration:** Days 1–3 | **Cost:** $79 one-time | **Owner:** Tech Lead

#### Objectives
Get all third-party accounts approved and environment variables configured.

#### Tasks
- [ ] Register domain (uigllc.org)
- [ ] Create Twilio account → apply for WhatsApp Business API
  - Submit business name: United Investing Group LLC
  - Sender name: Philip George
  - Expected approval: 3–5 business days
- [ ] Create Anthropic account → generate API key → add $20 credit
- [ ] Create SendGrid account → verify sender domain (philip.george@uigllc.org)
- [ ] Create HubSpot free account → note Portal ID + generate private app token
- [ ] Create Google Cloud project → enable Drive API → download service account JSON
- [ ] Create Supabase project → note DATABASE_URL
- [ ] Create Upstash Redis → note REDIS_URL
- [ ] Create Make.com account → subscribe to Core plan ($9)
- [ ] Clone repo, copy `.env.example` → `.env`, fill all values
- [ ] Run `docker-compose up` locally → confirm all 6 services start

#### Exit Criteria
All services start cleanly. `GET /api/analytics/overview` returns `200 OK`.

---

### PHASE 1: Data Foundation — Get 1,000 Leads in the Pipeline
**Duration:** Days 4–7 | **Cost:** ~$3 (Claude scoring) | **Owner:** Tech Lead + Philip

#### Objectives
Populate the pipeline with 1,000+ real leads via scraping and manual import.

#### Tasks

**1A — Import Existing Leads (Philip's collected leads)**
```bash
# Drop existing leads file into /data/
python scripts/import_leads.py --file data/collected_leads.csv --score --dry-run
# Review warnings, then:
python scripts/import_leads.py --file data/collected_leads.csv --score
```
- Expected: 100–500 leads depending on file size
- Verify deduplication works (check DB count)
- Confirm lead scores assigned (dashboard → AI Score distribution)

**1B — Run First Scrape Campaign (Airport Zones)**
```bash
# Preview the plan first
python scripts/run_scrape_campaign.py --cities DEL BOM BLR --dry-run

# Run live scrape (Delhi + Mumbai + Bengaluru)
python scripts/run_scrape_campaign.py \
  --cities DEL BOM BLR \
  --portals 99acres magicbricks nobroker \
  --pages 3
```
- Target: 400–600 fresh leads from Tier 1 cities
- Check `scrape_campaign_report.json` for results

**1C — Verify Lead Quality**
- Open dashboard at `http://localhost:3000`
- Confirm 1,000+ leads visible in Kanban board
- Check city distribution (should be spread across DEL, BOM, BLR)
- Confirm at least 70% have phone numbers

#### Exit Criteria
Database contains ≥1,000 leads. ≥700 have phone numbers. Dashboard loads correctly.

---

### PHASE 2: Outreach Engine Test — 50 Lead Pilot
**Duration:** Days 8–12 | **Cost:** ~$3 (50 WhatsApp + emails) | **Owner:** Tech Lead

#### Objectives
Validate the full outreach chain works end-to-end before scaling to 1,000.

#### Tasks

**2A — Dry-Run First**
```bash
python scripts/run_outreach_campaign.py \
  --min-score 70 --limit 50 --dry-run
```
Review which 50 leads would be contacted. Confirm names and phone numbers look real.

**2B — Send Pilot Outreach**
```bash
python scripts/run_outreach_campaign.py \
  --min-score 70 --limit 50 --city "Delhi NCR"
```

**2C — Monitor Deliverability**
- Twilio console: Check WhatsApp delivery receipts
- SendGrid activity: Confirm email open rates
- DB check: 50 leads should be at `contact_initiated` stage
- Make.com: Confirm follow-up tasks scheduled for Day 3 and Day 7

**2D — Test Inbound Response Handling**
- Reply to one test WhatsApp message from a test number
- Confirm webhook fires (`POST /webhooks/twilio`)
- Confirm lead stage advances to `response_received`
- Confirm document request WhatsApp auto-sends

**2E — Test Document Upload**
- Upload a test PDF to `POST /api/documents/upload`
- Confirm Google Drive folder created
- Confirm Claude Vision analysis runs
- Confirm `check_docs_complete` evaluates completeness

#### Exit Criteria
50 leads contacted, at least 1 progresses through response → docs_requested → under_verification. Zero crash errors in logs.

---

### PHASE 3: Full Pipeline Run — 1,000 Leads
**Duration:** Days 13–21 | **Cost:** ~$13 | **Owner:** Tech Lead + Philip

#### Objectives
Run the full 1,000 lead outreach campaign, validate automation end-to-end, and identify any scaling bottlenecks.

#### Tasks

**3A — Activate Make.com Blueprint**
- Import `docs/make-com-blueprint.json` into Make.com
- Set environment variables: `BACKEND_URL`, `UIG_INTERNAL_API_KEY`, `DASHBOARD_URL`
- Create webhook → copy URL → add to `.env` as `MAKE_WEBHOOK_URL`
- Enable the scenario and run a test trigger

**3B — Full Campaign Launch**
```bash
# High-quality leads first (score ≥70)
python scripts/run_outreach_campaign.py --min-score 70 --limit 500

# Next day: mid-tier leads (score 40-69)
python scripts/run_outreach_campaign.py --min-score 40 --limit 500
```
Recommended: split over 2 days to stay within Twilio rate limits and review results.

**3C — Monitor for 7 Days**
Track daily:
- Lead stage progression (new_lead → contact_initiated → response_received)
- Response rate target: ≥5% (50+ responses from 1,000 outreach)
- Conversion target: ≥10 leads reach `qualified` stage
- Document collection: ≥5 leads upload at least 1 document

**3D — HubSpot Sync Verification**
- Login to HubSpot → Contacts
- Confirm all 1,000 leads synced with correct pipeline stages
- Confirm at least 1 deal created in HubSpot for approved leads

**3E — LPI Certificate Test**
```bash
# Test issue + verify
curl -X POST http://localhost:8000/api/lpi/issue \
  -H "Content-Type: application/json" \
  -d '{"lat": 28.5562, "lon": 77.1000, "owner_name": "Test Owner", "city": "Delhi"}'

# Verify code returned
curl http://localhost:8000/api/lpi/verify/LPI-IN-DL-XXXXXX-XXXXXX-XXXX
```

#### Exit Criteria
1,000 leads contacted. ≥50 responses. ≥10 qualified leads. ≥1 full end-to-end pipeline completion (new_lead → approved). HubSpot synced. No data loss.

---

### PHASE 4: Dashboard & Investor Demo Prep
**Duration:** Days 22–28 | **Cost:** $0 | **Owner:** Philip + Tech Lead

#### Objectives
Polish the dashboard, prepare the investor demo script, and document the pipeline results.

#### Tasks

**4A — Dashboard Health Check**
- `GET /api/analytics/overview` — confirm all KPIs render
- `GET /api/analytics/funnel` — conversion rates visible
- `GET /api/analytics/outreach` — channel performance chart
- Kanban board: all 11 stages visible with lead counts

**4B — Investor Demo Script**

*Demo Flow (15 minutes):*
1. **Open Dashboard** — Show live lead counts, pipeline funnel, outreach stats
2. **Show Kanban Board** — Walk through stages, explain automation at each stage
3. **Live Lead Scoring Demo** — Score a new lead live via API
4. **WhatsApp Outreach Demo** — Trigger an outreach message to a test number live
5. **LPI Certificate Demo** — Issue an LPI certificate for a Delhi airport-zone parcel
6. **Document Verification Demo** — Upload a test document, show AI analysis
7. **HubSpot Integration** — Show contact + deal in HubSpot synced in real-time

**4C — Key Metrics to Highlight for Investors**
- Total leads in pipeline: 1,000+
- Cities covered: 3 Tier-1 (Delhi, Mumbai, Bengaluru)
- Airport zones mapped: 28 across India
- Outreach cost per lead: <$0.02
- Time to first contact after lead creation: <2 minutes (automated)
- Monthly recurring cost to run at full scale: <$150
- Total setup cost: <$500
- Pipeline from lead to deal: fully automated, zero manual steps for initial outreach

**4D — Produce Demo Data Package**
- Export pipeline CSV from `GET /api/leads?format=csv`
- Screenshot dashboard with 1,000 leads
- HubSpot screenshot with synced contacts
- Sample WhatsApp conversation screenshot
- Sample LPI certificate (PDF or JSON)

#### Exit Criteria
Demo script rehearsed. All dashboard pages load under 3 seconds. Investor demo runs smoothly end-to-end in under 15 minutes.

---

### PHASE 5: Production Hardening (Post-Demo)
**Duration:** Weeks 6–8 | **Cost:** +$50/month | **Owner:** Tech Lead

*Begin only after investor feedback and funding confirmation.*

#### Scope
- Add Nginx reverse proxy + HTTPS (Let's Encrypt)
- Enable Celery Flower monitoring dashboard
- Set up error alerting (Sentry free tier)
- Enable Supabase Pro plan for production database
- Add rate limiting to FastAPI endpoints
- Run full Alembic migration on production database
- Set up automated daily DB backups via Supabase
- Expand to Tier 2 cities (HYD, MAA, CCU, PNQ)

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Twilio WhatsApp API approval delay | Medium | High | Apply Day 1; use SMS as fallback |
| Portal scraping blocked (IP ban) | Medium | Medium | Use Apify proxies; rotate user agents |
| Low lead response rate (<2%) | Low | Medium | Improve templates; add more follow-ups |
| Claude API rate limits | Low | Low | Batch scoring; async queue |
| HubSpot free tier limits | Low | Low | Free tier supports unlimited contacts |
| Make.com ops overage | Low | Low | Monitor; upgrade to $16/mo if needed |
| RERA / legal questions from leads | Medium | Medium | Philip George handles personally; have FAQ ready |

---

## Team & Responsibilities

| Role | Responsibility |
|------|---------------|
| **Philip George** | Lead communication, investor demo, outreach copy review |
| **Tech Lead** | Infrastructure setup, deployment, debugging |
| **Both** | Phase 1 lead data quality review, Phase 4 demo rehearsal |

*MVP can be operated by 1 person (Philip) after initial setup is complete.*

---

## Success Metrics for Investor Demo

| Metric | Target | Stretch |
|--------|--------|---------|
| Leads in pipeline | 1,000 | 2,500 |
| Cities covered | 3 | 6 |
| Response rate | 5% (50 leads) | 10% |
| Qualified leads | 10 | 25 |
| Leads with documents | 3 | 10 |
| End-to-end automation | Yes | Yes |
| Dashboard live | Yes | Yes |
| HubSpot synced | Yes | Yes |
| LPI certificates issued | 5 | 25 |
| Cost per lead | <$0.02 | <$0.01 |

---

## Budget Summary

| Phase | Duration | Cost |
|-------|----------|------|
| Phase 0: Setup | Days 1–3 | $79 one-time |
| Phase 1: Data (1,000 leads) | Days 4–7 | $3 |
| Phase 2: Pilot (50 leads) | Days 8–12 | $3 |
| Phase 3: Full Campaign | Days 13–21 | $13 |
| Phase 4: Demo Prep | Days 22–28 | $0 |
| Monthly Infra (2 months) | Ongoing | $198 |
| **TOTAL TO INVESTOR DEMO** | **~5 weeks** | **~$296** |

**Minimum to launch and demo: ~$300.**
**Monthly burn at MVP scale: ~$99/month.**
**Burn at 10,000 leads/month: ~$350/month.**

---

*Document prepared for internal use only. Do not distribute externally.*
*United Investing Group LLC | Philip George, Head of Asia Pacific*
