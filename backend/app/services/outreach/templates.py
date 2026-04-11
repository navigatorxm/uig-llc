"""
Message templates for ICP3A / UIG outreach — sender: Philip George.

Chain 1 — Initial outreach + 5 follow-ups within 48 hours
  T+0h   : initial_contact_whatsapp + initial_contact_email
  T+8h   : follow_up_1_whatsapp
  T+16h  : follow_up_2_whatsapp
  T+24h  : follow_up_3_whatsapp
  T+36h  : follow_up_4_whatsapp
  T+48h  : follow_up_5_whatsapp  (final)
  T+72h  : → cold_lead stage if still no response

Chain 2 — Document collection (triggered on qualified stage)
  T+0h   : document_request_whatsapp + document_request_email
  T+48h  : doc_follow_up_1_whatsapp
  T+120h : doc_follow_up_2_whatsapp  (5 days)
  T+240h : doc_follow_up_3_whatsapp  (10 days, final)
  T+336h : → pending_docs stage if docs still incomplete

Chain 3 — Verification outcome (triggered when all docs received)
  T+0h   : Claude Vision analysis begins
  T+72h  : approval_notification_whatsapp  OR  rejection_notification_whatsapp
           OR  missing_docs_request_whatsapp (partial pass)
"""
from typing import Dict, Tuple, Union
from app.config import settings

SENDER_SIGNATURE = (
    f"\n\nWarm regards,\n"
    f"{settings.sender_name}\n"
    f"{settings.sender_title}\n"
    f"{settings.sender_company}\n"
    f"{settings.sender_website}"
)

# =============================================================================
# CHAIN 1 — INITIAL OUTREACH + 5 FOLLOW-UPS
# =============================================================================

WHATSAPP_TEMPLATES: Dict[str, str] = {

    # ── T+0h ─────────────────────────────────────────────────────────────────
    "initial_contact_whatsapp": (
        "Hello {owner_name},\n\n"
        "I'm Philip George, Property Acquisition Manager and Head of Asia Pacific at "
        "United Investing Group LLC (UIG) — a diversified global conglomerate.\n\n"
        "We came across your property listing at *{property_address}* and are genuinely "
        "interested in exploring a *{transaction_type}* arrangement.\n\n"
        "Could you share:\n"
        "• Your expected price / rental terms\n"
        "• Any specific conditions\n"
        "• Your preferred timeline\n\n"
        "We move quickly and work with serious intent."
        + SENDER_SIGNATURE
    ),

    # ── T+8h — light check-in ─────────────────────────────────────────────────
    "follow_up_1_whatsapp": (
        "Hello {owner_name},\n\n"
        "Just checking if my earlier message reached you regarding the property at "
        "*{property_address}*.\n\n"
        "We're actively looking in this area and would love a quick 5-minute conversation "
        "to understand your expectations.\n\n"
        "Please feel free to reply here at any time."
        + SENDER_SIGNATURE
    ),

    # ── T+16h — value-angle follow-up ────────────────────────────────────────
    "follow_up_2_whatsapp": (
        "Hello {owner_name},\n\n"
        "I wanted to share a bit more about why we're reaching out about *{property_address}*.\n\n"
        "UIG is one of the few buyers with a *dedicated India acquisition mandate* for "
        "properties near major airport zones. We offer:\n"
        "✓ Fair market valuations with no haggling\n"
        "✓ Legally clean, documented process\n"
        "✓ Quick decisions — usually within 7 days of first meeting\n\n"
        "Even if you're not actively looking to sell right now, a conversation costs nothing."
        + SENDER_SIGNATURE
    ),

    # ── T+24h — Day 2 fresh opener ───────────────────────────────────────────
    "follow_up_3_whatsapp": (
        "Good morning {owner_name},\n\n"
        "I'm reaching out once more about your property at *{property_address}*.\n\n"
        "We have an open acquisition budget for properties in this zone and are looking to "
        "move decisively this week. If a {transaction_type} discussion is something you'd "
        "consider — even tentatively — I'd love to hear from you."
        + SENDER_SIGNATURE
    ),

    # ── T+36h — urgency + social proof ───────────────────────────────────────
    "follow_up_4_whatsapp": (
        "Hello {owner_name},\n\n"
        "Our team has recently completed acquisitions near {city_or_area} and we're "
        "expanding our portfolio in this corridor.\n\n"
        "Owners we've worked with have appreciated the speed and transparency of our process — "
        "no delays, no last-minute price changes.\n\n"
        "If {property_address} is still available, please do get in touch. We're happy to "
        "work around your schedule."
        + SENDER_SIGNATURE
    ),

    # ── T+48h — final, direct ─────────────────────────────────────────────────
    "follow_up_5_whatsapp": (
        "Hello {owner_name},\n\n"
        "This is my final message regarding your property at *{property_address}*.\n\n"
        "UIG remains interested. If you ever decide to explore a {transaction_type} — "
        "now or in the future — please reach out directly.\n\n"
        "We'll keep your details on file and will not contact you further unless you reach out."
        + SENDER_SIGNATURE
    ),

    # ==========================================================================
    # CHAIN 2 — DOCUMENT COLLECTION
    # ==========================================================================

    # ── T+0h after qualified ──────────────────────────────────────────────────
    "document_request_whatsapp": (
        "Hello {owner_name},\n\n"
        "Thank you for your interest in proceeding with United Investing Group LLC.\n\n"
        "To move forward with the *{transaction_type}* of your property at *{property_address}*, "
        "please share the following documents:\n\n"
        "{doc_list}\n\n"
        "📌 *Note:* The LPI Certificate is *mandatory* for all transactions in airport zones. "
        "If you don't have one, we can help you obtain it — just let us know.\n\n"
        "You can send documents as photos or PDFs directly here on WhatsApp. "
        "All documents are handled with complete confidentiality.\n\n"
        "Our legal team will review within *3–5 business days* of receiving the full set."
        + SENDER_SIGNATURE
    ),

    # ── T+48h — first doc follow-up ──────────────────────────────────────────
    "doc_follow_up_1_whatsapp": (
        "Hello {owner_name},\n\n"
        "Just a gentle reminder about the documents we requested for *{property_address}*.\n\n"
        "We've received *{docs_received_count} of {docs_total_count}* documents so far. "
        "The following are still pending:\n\n"
        "{missing_docs}\n\n"
        "Please share at your earliest convenience so we can keep your application moving. "
        "Do let us know if you need any help obtaining any of these."
        + SENDER_SIGNATURE
    ),

    # ── T+120h (5 days) — second doc follow-up ────────────────────────────────
    "doc_follow_up_2_whatsapp": (
        "Hello {owner_name},\n\n"
        "We're still waiting on a few documents to complete the review for *{property_address}*.\n\n"
        "Missing documents:\n"
        "{missing_docs}\n\n"
        "⏳ Our legal team's slot is currently reserved for your file. Once we receive the "
        "full set, the review starts immediately. Please try to share by end of this week."
        + SENDER_SIGNATURE
    ),

    # ── T+240h (10 days) — final doc follow-up ───────────────────────────────
    "doc_follow_up_3_whatsapp": (
        "Hello {owner_name},\n\n"
        "This is our final follow-up on the document submission for *{property_address}*.\n\n"
        "We still require:\n"
        "{missing_docs}\n\n"
        "If we don't receive these within *4 days*, we'll need to pause this file and "
        "re-allocate our team's capacity. You're always welcome to re-initiate when ready.\n\n"
        "If there's a specific difficulty obtaining any document — let us know and we'll help."
        + SENDER_SIGNATURE
    ),

    # ==========================================================================
    # CHAIN 3 — VERIFICATION OUTCOMES
    # ==========================================================================

    "approval_notification_whatsapp": (
        "Hello {owner_name},\n\n"
        "Great news! 🎉 After reviewing all documents for *{property_address}*, "
        "our legal team has cleared the file and given us the *green light* to proceed.\n\n"
        "Next steps:\n"
        "1️⃣ Site visit — please share *2–3 available time slots* this week or next\n"
        "2️⃣ Agreement term discussion — we'll share a draft for your review\n"
        "3️⃣ Signing & payment as per agreed schedule\n\n"
        "We're excited to move forward. What dates work best for the site visit?"
        + SENDER_SIGNATURE
    ),

    "rejection_notification_whatsapp": (
        "Hello {owner_name},\n\n"
        "Thank you sincerely for your time and cooperation throughout this process.\n\n"
        "After careful legal review, we regret to inform you that we are unable to proceed "
        "with the {transaction_type} of *{property_address}* at this time due to "
        "{rejection_reason}.\n\n"
        "We appreciate your trust in United Investing Group LLC and hope to work "
        "with you on future opportunities."
        + SENDER_SIGNATURE
    ),

    "missing_docs_request_whatsapp": (
        "Hello {owner_name},\n\n"
        "Our legal team has completed the initial review of documents for *{property_address}*.\n\n"
        "We're almost there — just a few more items needed to complete the verification:\n\n"
        "{missing_docs}\n\n"
        "Please share these at your earliest so we can finalise the review and proceed to approval."
        + SENDER_SIGNATURE
    ),
}

# =============================================================================
# EMAIL TEMPLATES
# =============================================================================

EMAIL_TEMPLATES: Dict[str, Dict[str, str]] = {

    "initial_contact_email": {
        "subject": "Property Acquisition Interest – {property_address} | United Investing Group LLC",
        "body": (
            "Dear {owner_name},\n\n"
            "I hope this message finds you well.\n\n"
            "My name is Philip George, and I serve as the Property Acquisition Manager and "
            "Head of Asia Pacific at United Investing Group LLC (UIG) — a diversified global "
            "conglomerate with significant interests across real estate, technology, and finance.\n\n"
            "We came across your property at {property_address} and are very interested "
            "in exploring a potential {transaction_type} arrangement.\n\n"
            "We would appreciate the opportunity to understand:\n"
            "  • Your asking price / rental expectations\n"
            "  • Any preferred conditions or timeline\n"
            "  • A convenient time for a brief discussion\n\n"
            "UIG prides itself on transparent dealings, legal compliance, and timely execution. "
            "We look forward to a productive conversation.\n"
            + SENDER_SIGNATURE
        ),
    },

    "document_request_email": {
        "subject": "Document Submission Request — {property_address} | UIG LLC",
        "body": (
            "Dear {owner_name},\n\n"
            "Thank you for your positive response and willingness to proceed with "
            "United Investing Group LLC.\n\n"
            "To move forward with the {transaction_type} of your property at {property_address}, "
            "we require the following documents:\n\n"
            "{doc_list}\n\n"
            "IMPORTANT: The LPI Certificate is a mandatory requirement for all transactions "
            "in airport-adjacent zones and must be included. If you require assistance obtaining "
            "an LPI Certificate, please contact us — we can facilitate this at no additional cost.\n\n"
            "You may email the documents directly to this address or share via WhatsApp. "
            "All documents will be treated with strict confidentiality.\n\n"
            "Our legal team will complete the review within 3–5 business days of receiving "
            "all required documents.\n"
            + SENDER_SIGNATURE
        ),
    },

    "doc_follow_up_email": {
        "subject": "Pending Documents — {property_address} | UIG LLC",
        "body": (
            "Dear {owner_name},\n\n"
            "We hope all is well. This is a follow-up regarding the documents for "
            "{property_address}.\n\n"
            "We have received {docs_received_count} of {docs_total_count} documents. "
            "The following are still pending:\n\n"
            "{missing_docs}\n\n"
            "Please share the remaining documents at your earliest convenience so our "
            "legal team can complete the review without further delay.\n\n"
            "If you are facing any difficulty in obtaining a specific document, please let "
            "us know — we are happy to assist.\n"
            + SENDER_SIGNATURE
        ),
    },

    "approval_email": {
        "subject": "Legal Clearance Confirmed — Next Steps | {property_address}",
        "body": (
            "Dear {owner_name},\n\n"
            "We are delighted to inform you that our legal team has completed the review "
            "of all documents submitted for {property_address} and has issued a clearance.\n\n"
            "We would like to proceed with the following next steps:\n\n"
            "  1. SITE VISIT — Please share your availability for a property inspection "
            "at a time convenient to you.\n"
            "  2. AGREEMENT DRAFT — We will share a draft of the {transaction_type} agreement "
            "for your review.\n"
            "  3. SIGNING & PAYMENT — Per the agreed schedule, closing can occur within "
            "7–14 business days of the site visit.\n\n"
            "Please reply to this email or WhatsApp us with your preferred visit dates.\n"
            + SENDER_SIGNATURE
        ),
    },

    "rejection_email": {
        "subject": "Regarding Your Property at {property_address} | UIG LLC",
        "body": (
            "Dear {owner_name},\n\n"
            "Thank you for your time and for submitting documents for {property_address}.\n\n"
            "After careful review by our legal team, we regret to inform you that we are "
            "unable to proceed with the {transaction_type} at this time.\n\n"
            "Reason: {rejection_reason}\n\n"
            "We greatly appreciate your cooperation and trust in United Investing Group LLC. "
            "Should the situation change or should you have other properties to discuss, "
            "please do not hesitate to reach out.\n"
            + SENDER_SIGNATURE
        ),
    },
}

# =============================================================================
# STATE-SPECIFIC DOCUMENT CHECKLISTS
# Based on state revenue laws, RERA guidelines, and DGCA airport zone rules.
# All airport-zone transactions require DGCA/AAI NOC regardless of state.
# =============================================================================

STATE_DOCUMENT_CHECKLISTS: Dict[str, Dict[str, list]] = {

    # ── Delhi / NCR (DDA + Revenue Dept + MCD) ───────────────────────────────
    "delhi": {
        "buy": [
            "📄 Sale Deed (original + all chain documents — minimum 30 years)",
            "📋 Jamabandi / Mutation Entry (Revenue Department)",
            "🔍 Encumbrance Certificate — last 15 years (Sub-Registrar office)",
            "🏗️ Approved Building Plan (MCD / DDA / NDMC)",
            "✅ Completion Certificate / Occupancy Certificate",
            "💰 Property Tax Receipts — last 5 years",
            "🏘️ RWA / Society NOC (if applicable)",
            "🆔 Owner PAN Card + Aadhaar (both parties)",
            "✈️ DGCA / AAI NOC (mandatory for airport zone — 5km radius IGI)",
            "🛰️ LPI Certificate ⚠️ MANDATORY (ICP3A zone requirement)",
            "📜 Power of Attorney (if owner is NRI or acting through representative)",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest Property Tax Receipt",
            "📄 Previous Rent Agreement (if any)",
            "🏘️ Society / RWA NOC (if flat in society)",
            "✅ Occupancy Certificate",
            "✈️ DGCA / AAI NOC (airport zone — IGI)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Maharashtra / Mumbai (IGR Maharashtra + BMC) ──────────────────────────
    "maharashtra": {
        "buy": [
            "📄 Sale Deed (registered at IGR Maharashtra)",
            "🌾 7/12 Extract — Satbara (for plots / agricultural-converted land)",
            "🏙️ Property Card (urban areas — City Survey extract)",
            "🔍 Encumbrance Certificate (IGR portal — last 15 years)",
            "🏗️ Approved Building Plan (BMC / MCGM / PMRDA / CIDCO)",
            "✅ Commencement Certificate + Completion / OC (BMC)",
            "🏢 Society Share Certificate + NOC from Housing Society",
            "📋 Index II (registered document extract from Sub-Registrar)",
            "💰 Property Tax Receipts — last 5 years",
            "🆔 Owner PAN Card + Aadhaar",
            "🏛️ RERA Registration Certificate (under-construction projects)",
            "✈️ DGCA / AAI NOC (airport zone — CSIA/BOM, NBIA/PNQ)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest Property Tax Receipt",
            "🏢 Society Share Certificate + NOC",
            "📄 Previous Leave & License Agreement (if any)",
            "✅ Occupation Certificate",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Karnataka / Bengaluru (Kaveri portal + BBMP) ──────────────────────────
    "karnataka": {
        "buy": [
            "📄 Sale Deed (registered via Kaveri Online portal)",
            "📋 Khata Certificate + Khata Extract (BBMP / CMC / TMC)",
            "🌾 RTC — Record of Rights, Tenancy & Crops (plots / converted land)",
            "📑 Mutation Register Extract (Revenue Department)",
            "🔍 Encumbrance Certificate — last 15 years (Kaveri portal)",
            "🏗️ Approved Building Plan (BBMP / BDA / BMRDA)",
            "✅ Completion Certificate + Occupancy Certificate",
            "🏘️ Conversion Order (if agricultural land converted to residential/commercial)",
            "💰 Property Tax Receipts — last 5 years (BBMP portal)",
            "🆔 Owner PAN Card + Aadhaar",
            "✈️ DGCA / AAI NOC (airport zone — KIA/BLR or HAL)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "📋 Khata Certificate",
            "💰 Latest BBMP Property Tax Receipt",
            "🏘️ Society NOC (if applicable)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Telangana / Hyderabad (IGRS Telangana + GHMC) ─────────────────────────
    "telangana": {
        "buy": [
            "📄 Sale Deed (registered at IGRS Telangana)",
            "📋 Patta / Passbook (issued by Revenue Department, Mandal office)",
            "🔍 Encumbrance Certificate (IGRS portal — last 15 years)",
            "🏗️ Layout Approval (HMDA / GHMC / DTCP)",
            "🏗️ Building Permit + Completion Certificate",
            "💰 Property Tax Receipts — last 5 years (GHMC portal)",
            "🆔 Owner PAN Card + Aadhaar",
            "📑 Link Documents (chain of title)",
            "✈️ DGCA / AAI NOC (airport zone — RGIA/HYD)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest GHMC Property Tax Receipt",
            "📋 Patta / Passbook",
            "📄 Previous Rent Agreement (if any)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Tamil Nadu / Chennai (TNREGINET + CMDA) ───────────────────────────────
    "tamil_nadu": {
        "buy": [
            "📄 Sale Deed (registered at TNREGINET portal)",
            "🌾 Patta (revenue title document — Tahsildar office)",
            "📋 Chitta (land revenue record — classification of land)",
            "📑 Adangal / Town Survey Land Record",
            "🔍 Encumbrance Certificate (TNREGINET — last 15 years)",
            "🏗️ Building Plan Approval (CMDA / DTCP / Local Body)",
            "✅ Completion Certificate",
            "💰 Property Tax Receipts — last 5 years",
            "🆔 Owner PAN Card + Aadhaar",
            "🌿 Land Use Certificate (for CRZ / agricultural boundaries)",
            "✈️ DGCA / AAI NOC (airport zone — MAA/Chennai)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest Property Tax Receipt",
            "🌾 Patta",
            "📄 Previous Rent Agreement (if any)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── West Bengal / Kolkata (AIRIS + BL&LRO) ───────────────────────────────
    "west_bengal": {
        "buy": [
            "📄 Sale Deed (registered via AIRIS portal)",
            "📋 Record of Rights / Khatian (BL&LRO office)",
            "📑 Mutation Certificate (BL&LRO — transfer of revenue record)",
            "🔍 Encumbrance Certificate",
            "🏗️ Approved Building Plan (KMC / KMDA / Municipal body)",
            "✅ Completion Certificate",
            "💰 Property Tax Receipts — last 5 years",
            "🆔 Owner PAN Card + Aadhaar",
            "✈️ DGCA / AAI NOC (airport zone — NSCBI/CCU)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest KMC Property Tax Receipt",
            "📋 Khatian (Record of Rights)",
            "📄 Previous Rent Agreement (if any)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Goa (North Goa / South Goa — DoR Goa) ────────────────────────────────
    "goa": {
        "buy": [
            "📄 Sale Deed (registered at Sub-Registrar, DoR Goa)",
            "📋 Form I & XIV (land survey record — Directorate of Settlement & Land Records)",
            "🔍 Encumbrance Certificate",
            "🏗️ Building Construction License (TCP Department / Panchayat / CCP)",
            "✅ Completion & Occupation Certificate",
            "🌿 CRZ NOC (if coastal property — CRZ notification compliance)",
            "💰 Property Tax Receipts",
            "🆔 Owner PAN Card + Aadhaar",
            "✈️ DGCA / AAI NOC (airport zone — GOI/Dabolim or MOI/Mopa)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "📋 Form I & XIV",
            "💰 Latest Property Tax Receipt",
            "🌿 CRZ NOC (if applicable)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Kerala / Kochi (EREGIS + Panchayat / Corporation) ────────────────────
    "kerala": {
        "buy": [
            "📄 Sale Deed (registered via eRegis portal)",
            "🌾 Possession Certificate (Thandaper — Revenue Department)",
            "🔍 Encumbrance Certificate (eRegis portal — last 15 years)",
            "📋 Survey Sketch / Land Records (Revenue / Survey Department)",
            "🏗️ Building Permit (Panchayat / Municipality / Corporation)",
            "✅ Completion / Occupancy Certificate",
            "💰 Property Tax Receipts — last 5 years",
            "🆔 Owner PAN Card + Aadhaar",
            "✈️ DGCA / AAI NOC (airport zone — COK/Cochin)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "🌾 Possession Certificate",
            "💰 Latest Property Tax Receipt",
            "📄 Previous Rent Agreement (if any)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },

    # ── Default (generic pan-India baseline) ─────────────────────────────────
    "default": {
        "buy": [
            "📄 Sale Deed (registered at local Sub-Registrar)",
            "🔍 Encumbrance Certificate — last 15 years",
            "📋 Revenue / Title Document (Patta / Khata / Khatian as applicable)",
            "📑 Mutation Certificate",
            "🏗️ Approved Building Plan (local municipal body)",
            "✅ Completion & Occupancy Certificate",
            "💰 Property Tax Receipts — last 5 years",
            "🆔 Owner PAN Card + Aadhaar",
            "✈️ DGCA / AAI NOC (mandatory for airport zone properties)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
        "rent": [
            "🆔 Owner PAN Card + Aadhaar",
            "💰 Latest Property Tax Receipt",
            "📋 Revenue Title Document",
            "📄 Previous Rent Agreement (if any)",
            "✈️ DGCA / AAI NOC (airport zone)",
            "🛰️ LPI Certificate ⚠️ MANDATORY",
        ],
    },
}

# Map city / IATA code to state key
CITY_TO_STATE: Dict[str, str] = {
    # Delhi NCR
    "DEL": "delhi", "Delhi": "delhi", "New Delhi": "delhi",
    "Gurugram": "delhi", "Noida": "delhi", "Faridabad": "delhi", "Ghaziabad": "delhi",
    # Maharashtra
    "BOM": "maharashtra", "Mumbai": "maharashtra", "Pune": "maharashtra",
    "PNQ": "maharashtra", "Navi Mumbai": "maharashtra", "Thane": "maharashtra",
    # Karnataka
    "BLR": "karnataka", "Bengaluru": "karnataka", "Bangalore": "karnataka",
    # Telangana
    "HYD": "telangana", "Hyderabad": "telangana",
    # Tamil Nadu
    "MAA": "tamil_nadu", "Chennai": "tamil_nadu",
    # West Bengal
    "CCU": "west_bengal", "Kolkata": "west_bengal",
    # Goa
    "GOI": "goa", "Goa": "goa", "Panaji": "goa",
    # Kerala
    "COK": "kerala", "Kochi": "kerala",
    # Ahmedabad / Gujarat
    "AMD": "default", "Ahmedabad": "default",
}


def get_doc_checklist(state_or_city: str, transaction_type: str = "buy") -> str:
    """
    Return a formatted document checklist string for a given state/city and transaction type.
    Falls back to default if state not found.
    """
    state_key = CITY_TO_STATE.get(state_or_city, state_or_city.lower())
    checklist = STATE_DOCUMENT_CHECKLISTS.get(state_key, STATE_DOCUMENT_CHECKLISTS["default"])
    docs = checklist.get(transaction_type, checklist["buy"])
    return "\n".join(docs)


def render_template(
    template_key: str,
    context: dict,
    email: bool = False,
) -> Union[str, Tuple[str, str]]:
    """
    Render a WhatsApp or email template with context variables.

    For email=True, returns (subject, body) tuple.
    For WhatsApp, returns message string.

    Context keys vary by template — see template docstrings above.
    Missing keys fall back to empty string rather than raising KeyError.
    """
    if email:
        tpl = EMAIL_TEMPLATES.get(template_key, {})
        safe_ctx = {k: context.get(k, "") for k in _extract_keys(tpl.get("subject", "") + tpl.get("body", ""))}
        subject = tpl.get("subject", "").format_map(safe_ctx)
        body = tpl.get("body", "").format_map(safe_ctx)
        return subject, body
    else:
        tpl = WHATSAPP_TEMPLATES.get(template_key, "")
        safe_ctx = {k: context.get(k, "") for k in _extract_keys(tpl)}
        return tpl.format_map(safe_ctx)


def _extract_keys(template_str: str) -> list:
    """Extract all {variable_name} keys from a template string."""
    import string
    formatter = string.Formatter()
    return [field_name for _, field_name, _, _ in formatter.parse(template_str) if field_name]
