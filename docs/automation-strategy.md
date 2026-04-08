# UIG-ICP3A Lead Generation & Automation Strategy

---

## 1. LEAD SOURCES

| Source | Method | Volume Target |
|--------|--------|---------------|
| **Property Scrapers** | MagicBricks, 99Acres, NoBroker, Housing.com | 50,000+ listings/month |
| **LPI Portal** | Property owners applying for LPI cert | 5,000/month |
| **Agent Referrals** | RERA agents submitting leads | 2,000/month |
| **Website Forms** | uigllc.org "Sell to UIG" form | 1,000/month |
| **Direct Outreach** | WhatsApp/Email to previous sellers | Ongoing |
| **Offline** | Property expos, CREDAI events | Per event |

---

## 2. LEAD CONVERSION PIPELINE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UIG LEAD CONVERSION FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

LEAD SOURCE
     │
     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   NEW LEAD  │────▶│CONTACT_INITIATED│───▶│RESPONSE_    │
│  (Score 0-20)│     │(WhatsApp+Email│     │RECEIVED     │
└─────────────┘     │ sent)         │     │(Score 40-60)│
                    └──────────────┘     └──────┬──────┘
                                                 │
                    ┌──────────────┐            ▼
                    │   FOLLOW-UPS  │     ┌─────────────┐
                    │ (Day 3, 7, 14)│     │  QUALIFIED  │
                    └──────────────┘     │(Score 60+)  │
                                         └──────┬──────┘
                                                │
                    ┌──────────────┐            ▼
                    │  NO RESPONSE  │     ┌─────────────┐
                    │  → COLD leads │     │DOCS_REQUESTED│
                    └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐            ▼
                    │  REJECTED     │     ┌─────────────┐
                    │  → CLOSED_LOST│     │DOCS_RECEIVED│
                    └──────────────┘     └──────┬──────┘
                                                │
                    ┌──────────────┐            ▼
                    │  SITE VISIT   │     ┌─────────────┐
                    │  COMPLETED    │     │UNDER_       │
                    └──────────────┘     │VERIFICATION │
                                         └──────┬──────┘
                                                │
                    ┌──────────────┐            ▼
                    │  DEAL CLOSED  │     ┌─────────────┐
                    │  🎉           │     │  APPROVED   │
                    └──────────────┘     └──────┬──────┘
                                                │
                   ┌──────────────┐             ▼
                   │  RERA REG    │      ┌─────────────┐
                   │  COMPLIANCE  │      │VISIT_       │
                   └──────────────┘      │SCHEDULED    │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  CLOSED_WON │
                                         │    🎉       │
                                         └─────────────┘
```

---

## 3. AUTOMATED OUTREACH FLOWS

### 3A. WHATSAPP AUTOMATION

| Trigger | Template | Timing | Automation |
|---------|----------|--------|------------|
| New lead from scraper | `initial_contact_whatsapp` | Immediate | Auto-send |
| Lead added from LPI portal | `lpi_acquisition_pitch` | Immediate | Auto-send |
| No response (Day 3) | `follow_up_1_whatsapp` | +72 hours | Celery task |
| No response (Day 7) | `follow_up_2_whatsapp` | +168 hours | Celery task |
| No response (Day 14) | `final_follow_up_whatsapp` | +336 hours | Celery task |
| Lead responds "interested" | `document_request_whatsapp` | On response | Auto-trigger |
| Documents approved | `approval_notification_whatsapp` | On approval | Auto-trigger |
| Site visit scheduled | `site_visit_confirmation` | On scheduling | Auto-trigger |
| Deal closed | `deal_closed_thank_you` | On close | Auto-trigger |

#### WhatsApp Template: LPI Acquisition Pitch
```
Hello {owner_name},

I'm Philip George from United Investing Group LLC — we're establishing operations in {city} and looking for properties near the airport.

We partner with ICP3A (International Commercial Property Accreditation) for property verification. If you're considering selling, we'd like to offer you:

✓ Free LPI Certificate (worth ₹15,000) — we cover the cost
✓ Fair market valuation 
✓ Fast closing within 30 days
✓ Transparent documentation

Are you open to a brief conversation about your property at {address}?

Looking forward to hearing from you.

Warm regards,
Philip George
Property Acquisition Manager | UIG LLC
uigllc.org
```

### 3B. EMAIL AUTOMATION

| Trigger | Template | Timing |
|---------|----------|--------|
| New lead | `initial_contact_email` | Immediate |
| LPI applicant | `lpi_welcome_email` | Immediate |
| Document request | `document_request_email` | On qualification |
| Document received | `docs_received_confirmation` | On upload |
| Verification complete | `verification_result_email` | On verification |
| Site visit invite | `site_visit_email` | On approval |
| Deal closed | `closing_confirmation_email` | On close |

#### Email Template: LPI Welcome
```
Subject: Welcome — Your LPI Certificate Application | ICP3A

Dear {owner_name},

Thank you for applying for your LPI (LiDAR Property Identifier) Certificate through ICP3A.

Your Application Reference: {lpi_code}
Property: {property_address}
Estimated Turnaround: {turnaround_days} business days

WHAT HAPPENS NEXT:
1. Our satellite team verifies your property coordinates
2. LiDAR scan is retrieved and analyzed
3. Your LPI certificate is generated
4. You'll receive an email with the certificate PDF

IMPORTANT: UIG LLC is actively acquiring properties in {city} airport zone. 
As an LPI certificate holder, you may receive interest from verified buyers.

Need help? Reply to this email or call {support_phone}.

Best regards,
ICP3A Certification Team
certification@icp3a.org
```

---

## 4. LEAD SOURCE SPECIFIC FLOWS

### 4A. SCRAPER LEAD FLOW
```
Property Listed on Portal
         │
         ▼
   Scrape Listing
   (address, price, phone, photos)
         │
         ▼
   Validate Airport Zone (5km radius)
         │
         ▼
   Create Lead + Property Record
         │
         ▼
   AI Lead Scoring (0-100)
         │
         ▼
   ├─ Score < 30 → Low Priority Queue
   ├─ Score 30-60 → Standard Outreach  
   └─ Score > 60 → High Priority Outreach
         │
         ▼
   Send WhatsApp + Email
   (initial_contact)
         │
         ▼
   Schedule Follow-ups (Day 3, 7, 14)
```

### 4B. LPI PORTAL LEAD FLOW
```
Property Owner Visits uigllc.org/lpi
         │
         ▼
   Fills LPI Application Form
   (name, phone, email, address, property docs)
         │
         ▼
   Create Lead + LPI Request
         │
         ▼
   Send ICP3A Welcome Email
         │
         ▼
   Trigger LPI Certification Process
         │
         ▼
   Send UIG Acquisition Pitch
   (after LPI issued)
         │
         ▼
   If Owner Interested → Add to Outreach Pipeline
```

### 4C. AGENT REFERRAL LEAD FLOW
```
Agent Submits Lead via Portal
         │
         ▼
   Verify Agent (RERA check)
         │
         ▼
   Create Lead with Agent ID
         │
         ▼
   Send Agent Confirmation
         │
         ▼
   Process Lead normally
         │
         ▼
   On Deal Close:
   ├─ Pay Agent Referral Fee
   └─ Send Agent Commission Report
```

---

## 5. FOLLOW-UP AUTOMATION RULES

| Scenario | Action | Delay |
|----------|--------|-------|
| No response | Follow-up #1 | 72 hours |
| No response | Follow-up #2 | 168 hours (Day 7) |
| No response | Follow-up #3 + Call attempt | 336 hours (Day 14) |
| No response after 3 attempts | Mark "cold" → Agent nurture list | N/A |
| Response: "Not interested" | Send polite thank you | Immediate |
| Response: "Already sold" | Mark closed_lost | Immediate |
| Response: "Interested" | Advance to qualified | Immediate |

---

## 6. LEAD SCORING MODEL

| Factor | Weight | Criteria |
|--------|--------|----------|
| **Location** | 30% | Within 3km of airport = 30pts, 3-5km = 20pts, 5-10km = 10pts |
| **Price** | 20% | Below market = 20pts, At market = 15pts, Above = 10pts |
| **Property Type** | 15% | Commercial/Industrial = 15pts, Residential = 10pts |
| **Listing Freshness** | 15% | <7 days = 15pts, 7-30 days = 10pts, >30 days = 5pts |
| **Owner Contact Quality** | 10% | Has WhatsApp = 10pts, Phone only = 5pts |
| **Document Readiness** | 10% | Has docs ready = 10pts, No docs = 0pts |

**Score Thresholds:**
- 0-30: Cold lead (minimal outreach)
- 30-60: Warm lead (standard sequence)
- 60-100: Hot lead (priority outreach + call)

---

## 7. CONVERSION METRICS

| Stage | Target Conversion |
|-------|-------------------|
| Lead → Contact Initiated | 100% (auto) |
| Contact Initiated → Response | 15% |
| Response → Qualified | 60% |
| Qualified → Documents Submitted | 50% |
| Documents → Approved | 70% |
| Approved → Site Visit | 80% |
| Site Visit → Closed Won | 60% |

**Funnel Calculation:**
- 10,000 leads → 1,500 responses → 900 qualified → 450 docs → 315 approved → 252 visits → 151 deals

---

## 8. IMPLEMENTATION PRIORITY

### Phase 1: Core Automation (Week 1-2)
- [ ] WhatsApp initial contact on new lead
- [ ] Email initial contact on new lead
- [ ] Follow-up scheduling (Day 3, 7, 14)
- [ ] Lead scoring on creation

### Phase 2: Response Handling (Week 3-4)
- [ ] Auto-detect "interested" keywords
- [ ] Document request automation
- [ ] Stage transition automation
- [ ] HubSpot sync

### Phase 3: Advanced (Week 5-6)
- [ ] LPI portal lead integration
- [ ] Agent referral flow
- [ ] Call scheduling automation
- [ ] Deal closing workflow

---

## 9. KEY AUTOMATION ENDPOINTS

```
POST /api/leads              → Create lead + trigger outreach
PATCH /api/leads/{id}/stage  → Stage transition + side effects
POST /api/outreach/send      → Send WhatsApp/email
GET  /api/leads/{id}/score   → Get AI lead score
POST /api/webhooks/make      → Receive Make.com events
POST /api/webhooks/whatsapp  → Receive WhatsApp responses
```

---

## 10. MESSAGE TEMPLATES INDEX

### WhatsApp Templates
| Key | Purpose |
|-----|---------|
| `initial_contact_whatsapp` | First outreach to scraped leads |
| `lpi_acquisition_pitch` | Pitch to LPI applicants |
| `follow_up_1_whatsapp` | Day 3 follow-up |
| `follow_up_2_whatsapp` | Day 7 follow-up |
| `final_follow_up_whatsapp` | Day 14 final attempt |
| `document_request_whatsapp` | Request docs after qualification |
| `approval_notification_whatsapp` | Notify of approval |
| `site_visit_confirmation` | Confirm scheduled visit |
| `polite_decline` | Rejection message |

### Email Templates
| Key | Purpose |
|-----|---------|
| `initial_contact_email` | First email to leads |
| `lpi_welcome_email` | LPI application confirmation |
| `document_request_email` | Document request with list |
| `docs_received_confirmation` | Acknowledge doc upload |
| `site_visit_email` | Site visit invitation |
| `closing_confirmation_email` | Deal closed confirmation |

---

## 11. CELERY TASK SCHEDULE

```python
# outreach_tasks.py

@celery.task
def send_initial_outreach(lead_id: int):
    """Send initial WhatsApp + Email to new lead"""
    pass

@celery.task
def schedule_follow_ups(lead_id: int):
    """Schedule Day 3, 7, 14 follow-ups"""
    pass

@celery.task  
def process_follow_up(lead_id: int, follow_up_number: int):
    """Execute scheduled follow-up"""
    pass

@celery.task
def check_and_advance_stage(lead_id: int):
    """Check lead status and advance if needed"""
    pass

@celery.task
def sync_to_hubspot(lead_id: int):
    """Sync lead to HubSpot CRM"""
    pass
```

---

## 12. COLD LEAD NURTURE

Leads with no response after 14 days:
- Move to "Cold Lead" segment
- Monthly newsletter via email
- Periodic WhatsApp check-ins (quarterly)
- Offer: "Still interested? Reply for free property valuation"
- On response: Re-engage at qualified stage
