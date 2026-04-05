import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentType(str, enum.Enum):
    # Purchase documents
    sale_deed = "sale_deed"
    chain_docs = "chain_docs"
    encumbrance_cert = "encumbrance_cert"
    mutation_cert = "mutation_cert"
    approved_plan = "approved_plan"
    cc_oc = "cc_oc"
    tax_receipts = "tax_receipts"
    pan_aadhaar = "pan_aadhaar"
    society_docs = "society_docs"
    lpi_cert = "lpi_cert"
    # Rental documents
    rent_agreement = "rent_agreement"
    police_verification = "police_verification"
    # General
    other = "other"


PURCHASE_REQUIRED_DOCS = [
    DocumentType.sale_deed,
    DocumentType.chain_docs,
    DocumentType.encumbrance_cert,
    DocumentType.mutation_cert,
    DocumentType.approved_plan,
    DocumentType.cc_oc,
    DocumentType.tax_receipts,
    DocumentType.pan_aadhaar,
    DocumentType.society_docs,
    DocumentType.lpi_cert,  # MANDATORY
]

RENTAL_REQUIRED_DOCS = [
    DocumentType.rent_agreement,
    DocumentType.pan_aadhaar,
    DocumentType.police_verification,
]


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    doc_type = Column(Enum(DocumentType), nullable=False)

    google_drive_file_id = Column(String(255))
    google_drive_url = Column(Text)
    original_filename = Column(String(500))

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(255), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # AI analysis result
    ai_analysis = Column(Text, nullable=True)  # JSON string from Claude
    ai_flags = Column(Text, nullable=True)      # JSON list of issues

    lead = relationship("Lead", back_populates="documents")

    created_at = Column(DateTime, default=datetime.utcnow)
