from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.models.lead import Lead
from app.models.document import Document, DocumentType, PURCHASE_REQUIRED_DOCS, RENTAL_REQUIRED_DOCS
from app.schemas.document import (
    DocumentResponse, DocumentVerifyRequest,
    DocumentChecklistResponse, DocumentUploadResponse,
)
from app.services.storage.google_drive import GoogleDriveService
from app.services.verification.legal_checker import run_full_legal_check
from app.workers.verification_tasks import analyze_document, check_docs_complete
from app.auth.jwt import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    lead_id: int = Form(...),
    doc_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a property document to Google Drive and create a Document record."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    content = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    try:
        drive = GoogleDriveService()
        subfolder = f"Lead_{lead_id}_{lead.owner_name.replace(' ', '_')}"
        result = drive.upload_file(
            file_content=content,
            filename=f"{doc_type.value}_{file.filename}",
            mime_type=mime_type,
            subfolder_name=subfolder,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File upload failed: {exc}")

    doc = Document(
        lead_id=lead_id,
        doc_type=doc_type,
        google_drive_file_id=result["id"],
        google_drive_url=result["url"],
        original_filename=file.filename,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Kick off async AI analysis
    analyze_document.delay(doc.id)
    # Check if all docs are now complete
    check_docs_complete.delay(lead_id)

    return DocumentUploadResponse(
        document_id=doc.id,
        doc_type=doc_type.value,
        google_drive_url=result["url"],
        message="Document uploaded and queued for AI analysis",
    )


@router.get("/documents/{lead_id}", response_model=DocumentChecklistResponse)
def get_document_checklist(lead_id: int, db: Session = Depends(get_db)):
    """Get the document checklist status for a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    docs = db.query(Document).filter(Document.lead_id == lead_id).all()
    uploaded_types = {d.doc_type.value for d in docs}
    verified_types = {d.doc_type.value for d in docs if d.verified}

    prop = lead.properties[0] if lead.properties else None
    tx_type = prop.transaction_type.value if prop else "buy"
    required = PURCHASE_REQUIRED_DOCS if tx_type == "buy" else RENTAL_REQUIRED_DOCS
    required_values = [d.value for d in required]
    missing = [d for d in required_values if d not in uploaded_types]

    lpi_doc = next((d for d in docs if d.doc_type == DocumentType.lpi_cert and d.verified), None)

    return DocumentChecklistResponse(
        lead_id=lead_id,
        transaction_type=tx_type,
        required_docs=required_values,
        uploaded_docs=list(uploaded_types),
        verified_docs=list(verified_types),
        missing_docs=missing,
        lpi_verified=lpi_doc is not None,
        all_complete=len(missing) == 0,
    )


@router.post("/documents/{document_id}/verify", response_model=DocumentResponse)
def verify_document(
    document_id: int,
    verify_request: DocumentVerifyRequest,
    db: Session = Depends(get_db),
):
    """Mark a document as verified (or rejected) by the legal team."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.verified = verify_request.verified
    doc.verified_at = datetime.now(timezone.utc)
    doc.verified_by = verify_request.verified_by
    doc.rejection_reason = verify_request.rejection_reason
    db.commit()
    db.refresh(doc)

    return doc


@router.post("/documents/{lead_id}/legal-check")
def run_legal_check(lead_id: int, transaction_type: str = "buy", db: Session = Depends(get_db)):
    """Run full legal compliance check for a lead."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return run_full_legal_check(lead_id, transaction_type, db)
