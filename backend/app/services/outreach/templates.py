"""Message templates for UIG outreach — sender: Philip George."""
from typing import Tuple
from app.config import settings

SENDER_SIGNATURE = (
    f"\n\nWarm regards,\n"
    f"{settings.sender_name}\n"
    f"{settings.sender_title}\n"
    f"{settings.sender_company}\n"
    f"{settings.sender_website}"
)

WHATSAPP_TEMPLATES = {
    "initial_contact_whatsapp": (
        "Hello {owner_name},\n\n"
        "I'm Philip George, Property Acquisition Manager and Head of Asia Pacific at "
        "United Investing Group LLC (UIG) — a diversified global conglomerate.\n\n"
        "We came across your property listing at *{property_address}* and are genuinely interested "
        "in exploring a potential *{transaction_type}* arrangement.\n\n"
        "Could you share:\n"
        "• Your expected price / rental terms\n"
        "• Any specific conditions\n"
        "• Your preferred timeline\n\n"
        "We move quickly and work with serious intent."
        + SENDER_SIGNATURE
    ),

    "follow_up_1_whatsapp": (
        "Hello {owner_name},\n\n"
        "I had reached out a few days ago regarding your property at *{property_address}*.\n\n"
        "We at United Investing Group LLC remain interested in a {transaction_type} discussion. "
        "Please do let us know if you're open to a conversation — even a brief call would help us "
        "understand your expectations.\n\n"
        "Looking forward to hearing from you."
        + SENDER_SIGNATURE
    ),

    "follow_up_2_whatsapp": (
        "Hello {owner_name},\n\n"
        "This is my final follow-up regarding your property at *{property_address}*.\n\n"
        "UIG is actively acquiring properties in Delhi NCR. We offer *fair valuations, "
        "transparent documentation, and timely closures*. If your plans for this property "
        "have changed or you'd like a no-obligation discussion, we're available at short notice.\n\n"
        "Feel free to reply here or call us directly."
        + SENDER_SIGNATURE
    ),

    "document_request_whatsapp": (
        "Hello {owner_name},\n\n"
        "Thank you for your interest in proceeding with United Investing Group LLC.\n\n"
        "As the next step, we kindly request the following documents for the *{transaction_type}* "
        "of your property:\n\n"
        "{doc_list}\n\n"
        "Please share scanned/photo copies at your earliest convenience. "
        "All documents will be handled with complete confidentiality.\n\n"
        "Once received, our legal team will conduct a review within 3-5 business days."
        + SENDER_SIGNATURE
    ),

    "approval_notification_whatsapp": (
        "Hello {owner_name},\n\n"
        "Great news! After reviewing all documents for your property at *{property_address}*, "
        "our legal team has given the *green light* to proceed.\n\n"
        "We would like to schedule:\n"
        "1. A site visit at your convenience\n"
        "2. Finalization of the agreement terms\n\n"
        "Please share 2-3 available time slots and we will confirm promptly."
        + SENDER_SIGNATURE
    ),

    "rejection_notification_whatsapp": (
        "Hello {owner_name},\n\n"
        "Thank you for your time and cooperation throughout this process.\n\n"
        "After careful review, we regret to inform you that we are unable to proceed "
        "with this particular property at this time.\n\n"
        "We appreciate your trust in United Investing Group LLC and hope to work "
        "with you in future opportunities."
        + SENDER_SIGNATURE
    ),
}

EMAIL_TEMPLATES = {
    "initial_contact_email": {
        "subject": "Property Acquisition Interest – {property_address} | United Investing Group LLC",
        "body": (
            "Dear {owner_name},\n\n"
            "I hope this message finds you well.\n\n"
            "My name is Philip George, and I serve as the Property Acquisition Manager and "
            "Head of Asia Pacific at United Investing Group LLC (UIG) — a diversified global "
            "conglomerate with significant interests across real estate, technology, and finance.\n\n"
            "We came across your property listing at {property_address} and are very interested "
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
            "Please note that the *LPI Certificate* is a mandatory requirement for all purchase "
            "transactions in Delhi NCR and must be included.\n\n"
            "You may email the documents directly to this address or share via WhatsApp. "
            "All documents will be treated with strict confidentiality.\n\n"
            "Our legal team will complete the review within 3-5 business days of receiving "
            "all required documents.\n"
            + SENDER_SIGNATURE
        ),
    },
}


def render_template(template_key: str, context: dict, email: bool = False) -> str | Tuple[str, str]:
    """
    Render a message template with context variables.
    For email=True, returns (subject, body) tuple.
    """
    if email:
        template = EMAIL_TEMPLATES.get(template_key, {})
        subject = template.get("subject", "").format(**context)
        body = template.get("body", "").format(**context)
        return subject, body
    else:
        template = WHATSAPP_TEMPLATES.get(template_key, "")
        return template.format(**context)
