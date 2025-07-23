from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Document identification
    document_type = Column(String(50), nullable=False)
    # Certificate of Compliance, Commercial Invoice, Packing List,
    # Bill of Lading, Airway Bill, Certificate of Origin,
    # Test Certificate, Material Certificate, Photo, Email, Other

    document_category = Column(String(30))  # Compliance, Financial, Shipping, Quality, Communication

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash for integrity

    # Document details
    title = Column(String(200))
    description = Column(Text)
    document_number = Column(String(100))  # Certificate number, invoice number, etc.
    version = Column(String(20), default="1.0")

    # Dates
    document_date = Column(DateTime)  # Date on the document
    issue_date = Column(DateTime)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)

    # Compliance and certification
    is_compliance_document = Column(Boolean, default=False)
    compliance_standard = Column(String(100))  # AS9100, ISO 9001, EASA Part 21, etc.
    issuing_authoritiy = Column(String(200))  # Who issued the certificate
    certificate_scope = Column(Text)

    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(20), default="Not Required")
    # Not Required, Pending, Approved, Rejected, Conditional

    approved_by = Column(String(100))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)
    rejection_reason = Column(Text)

    # Quality and verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(100))
    verification_date = Column(DateTime)
    verification_method = Column(String(50))  # Visual, Third Party, Self-Certified

    # Access control
    is_confidential = Column(Boolean, default=False)
    access_level = Column(String(20), default="Internal")  # Public, Internal, Restricted, Confidential
    allowed_roles = Column(String(200))  # Comma-separated list of roles

    # Revision tracking
    is_latest_version = Column(Boolean, default=True)
    superseded_by_id = Column(Integer, ForeignKey("documents.id"))
    supersedes_id = Column(Integer, ForeignKey("documents.id"))

    # Tags and search
    tags = Column(String(500))  # Comma-separated tags for easy searching
    searchable_content = Column(Text)  # Extracted text content for full-text search

    # Digital signature and security
    is_digitally_signed = Column(Boolean, default=False)
    digital_signature_valid = Column(Boolean)
    signature_timestamp = Column(DateTime)

    # Metadata
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime)
    access_count = Column(Integer, default=0)

    # Relationships
    order = relationship("Order", back_populates="documents")
    superseded_by = relationship("Document", remote_side=[id], foreign_keys=[superseded_by_id])
    supersedes = relationship("Document", remote_side=[id], foreign_keys=[supersedes_id])
