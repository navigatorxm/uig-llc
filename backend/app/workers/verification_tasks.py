"""Celery tasks for document verification."""
import logging
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.lead import Lead, PipelineStage
from app.models.document import Document, DocumentType

logger = logging.getLogger(__name__)


@celery_app.task
def analyze_document(document_id: int):
    """Run AI analysis on an uploaded document."""
    from app.services.ai.document_analyzer import DocumentAnalyzer

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc or not doc.google_drive_file_id:
            return

        analyzer = DocumentAnalyzer()
        result = analyzer.analyze(doc.google_drive_file_id, doc.doc_type.value)

        doc.ai_analysis = str(result.get("analysis", ""))
        import json
        doc.ai_flags = json.dumps(result.get("flags", []))
        db.commit()
        logger.info(f"Document {document_id} analyzed: {len(result.get('flags', []))} flags")

    except Exception as exc:
        db.rollback()
        logger.error(f"Document analysis failed for {document_id}: {exc}")
    finally:
        db.close()


@celery_app.task
def check_docs_complete(lead_id: int):
    """Check if all required documents are uploaded, notify team if so."""
    from app.services.outreach.email import EmailService
    from app.models.document import PURCHASE_REQUIRED_DOCS, RENTAL_REQUIRED_DOCS

    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return

        docs = db.query(Document).filter(Document.lead_id == lead_id).all()
        uploaded_types = {d.doc_type for d in docs}

        # Determine required docs based on deal type
        prop = lead.properties[0] if lead.properties else None
        if prop and prop.transaction_type.value == "rent":
            required = set(RENTAL_REQUIRED_DOCS)
        else:
            required = set(PURCHASE_REQUIRED_DOCS)

        missing = required - uploaded_types

        if not missing:
            lead.pipeline_stage = PipelineStage.docs_received
            db.commit()

            # Notify verification team
            EmailService().send_internal(
                subject=f"Documents Complete — Lead #{lead_id}: {lead.owner_name}",
                body=f"All required documents have been received for lead {lead_id}.\n"
                     f"Owner: {lead.owner_name}\nPhone: {lead.phone}\n"
                     f"Please proceed with verification.",
            )
            logger.info(f"Lead {lead_id} docs complete — stage advanced to docs_received")
        else:
            logger.info(f"Lead {lead_id} still missing: {[d.value for d in missing]}")

    except Exception as exc:
        db.rollback()
        logger.error(f"Docs check failed for lead {lead_id}: {exc}")
    finally:
        db.close()
