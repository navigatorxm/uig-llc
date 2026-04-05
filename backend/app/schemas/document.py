from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentType


class DocumentResponse(BaseModel):
    id: int
    lead_id: int
    doc_type: DocumentType
    google_drive_file_id: Optional[str] = None
    google_drive_url: Optional[str] = None
    original_filename: Optional[str] = None
    uploaded_at: datetime
    verified: bool
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    ai_flags: Optional[str] = None

    model_config = {"from_attributes": True}


class DocumentVerifyRequest(BaseModel):
    verified: bool
    verified_by: str
    rejection_reason: Optional[str] = None


class DocumentChecklistResponse(BaseModel):
    lead_id: int
    transaction_type: str
    required_docs: List[str]
    uploaded_docs: List[str]
    verified_docs: List[str]
    missing_docs: List[str]
    lpi_verified: bool
    all_complete: bool


class DocumentUploadResponse(BaseModel):
    document_id: int
    doc_type: str
    google_drive_url: str
    message: str
