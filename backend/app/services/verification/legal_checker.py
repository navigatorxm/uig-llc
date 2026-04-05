"""Legal compliance checker for Delhi NCR property documents."""
import json
import logging
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentType, PURCHASE_REQUIRED_DOCS, RENTAL_REQUIRED_DOCS
from app.models.lead import Lead

logger = logging.getLogger(__name__)


def check_document_completeness(
    lead_id: int,
    transaction_type: str,
    db: Session,
) -> Tuple[bool, List[str]]:
    """
    Check if all required documents are present and verified.
    Returns (is_complete, list_of_missing_doc_types).
    """
    docs = db.query(Document).filter(Document.lead_id == lead_id).all()
    uploaded_types = {d.doc_type for d in docs}

    required = set(PURCHASE_REQUIRED_DOCS if transaction_type == "buy" else RENTAL_REQUIRED_DOCS)
    missing = required - uploaded_types

    return len(missing) == 0, [d.value for d in missing]


def verify_lpi_certificate(lead_id: int, db: Session) -> Tuple[bool, str]:
    """
    Critical check: verify the LPI certificate is present and AI-validated.
    Returns (is_valid, reason).
    """
    lpi_doc = (
        db.query(Document)
        .filter(
            Document.lead_id == lead_id,
            Document.doc_type == DocumentType.lpi_cert,
        )
        .first()
    )

    if not lpi_doc:
        return False, "LPI Certificate not uploaded"

    if lpi_doc.rejection_reason:
        return False, f"LPI Certificate rejected: {lpi_doc.rejection_reason}"

    # Check AI analysis for validity
    if lpi_doc.ai_analysis:
        try:
            analysis = json.loads(lpi_doc.ai_analysis)
            if analysis.get("is_valid") is False:
                return False, "LPI Certificate marked invalid by AI analysis"
            if analysis.get("recommendation") == "reject":
                flags = analysis.get("flags", [])
                return False, f"LPI Certificate rejected: {', '.join(flags)}"
        except json.JSONDecodeError:
            pass

    if not lpi_doc.verified:
        return False, "LPI Certificate not yet verified by legal team"

    return True, "LPI Certificate valid"


def run_full_legal_check(
    lead_id: int,
    transaction_type: str,
    db: Session,
) -> dict:
    """
    Run all legal compliance checks for a lead.
    Returns structured result with approval/rejection decision.
    """
    results = {
        "lead_id": lead_id,
        "transaction_type": transaction_type,
        "checks": {},
        "approved": False,
        "rejection_reasons": [],
    }

    # 1. Document completeness
    is_complete, missing = check_document_completeness(lead_id, transaction_type, db)
    results["checks"]["document_completeness"] = {
        "passed": is_complete,
        "missing_docs": missing,
    }
    if not is_complete:
        results["rejection_reasons"].append(f"Missing documents: {', '.join(missing)}")

    # 2. LPI Certificate (purchase only — MANDATORY)
    if transaction_type == "buy":
        lpi_valid, lpi_reason = verify_lpi_certificate(lead_id, db)
        results["checks"]["lpi_certificate"] = {
            "passed": lpi_valid,
            "reason": lpi_reason,
        }
        if not lpi_valid:
            results["rejection_reasons"].append(lpi_reason)

    # 3. Check for any document AI flags
    docs = db.query(Document).filter(Document.lead_id == lead_id).all()
    flagged_docs = []
    for doc in docs:
        if doc.ai_flags:
            try:
                flags = json.loads(doc.ai_flags)
                if flags:
                    flagged_docs.append({
                        "doc_type": doc.doc_type.value,
                        "flags": flags,
                    })
            except json.JSONDecodeError:
                pass

    results["checks"]["ai_document_flags"] = {
        "passed": len(flagged_docs) == 0,
        "flagged_documents": flagged_docs,
    }
    if flagged_docs:
        results["rejection_reasons"].append(
            f"AI flags on: {', '.join(d['doc_type'] for d in flagged_docs)}"
        )

    # Final decision
    results["approved"] = len(results["rejection_reasons"]) == 0

    logger.info(
        f"Legal check for lead {lead_id}: "
        f"{'APPROVED' if results['approved'] else 'REJECTED'} "
        f"({len(results['rejection_reasons'])} issues)"
    )
    return results
