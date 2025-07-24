from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    project_code = Column(String(50), unique=True, nullable=False, index=True)

    # Client information
    client_name = Column(String(200), nullable=False)
    client_contact_person = Column(String(100))
    client_email = Column(String(255))
    client_phone = Column(String(50))

    # Project details
    description = Column(Text)
    project_type = Column(String(50))  # Aviation, Marine, Industrial, etc.
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    planned_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime)

    # Financial
    total_budget = Column(Numeric(precision=15, scale=2))
    currency = Column(String(3), default="QAR")
    budget_consumed = Column(Numeric(precision=15, scale=2), default=0)

    # Status and priority
    status = Column(String(20), default="Planning")  # Planning, Active, On Hold, Completed
    priority = Column(String(10), default="Normal")  # Low, Normal, High, Critical
    completion_percentage = Column(Integer, default=0)

    # Team assignments
    project_manager_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Location information
    installation_location = Column(String(200))
    installation_country = Column(String(100))
    installation_city = Column(String(100))

    # Compliance and certification
    requires_certification = Column(Boolean, default=False)
    certification_status = Column(String(50))  # Pending, In Progress, Approved, Rejected
    regulatory_authority = Column(String(100))  # QCAA, EASA, FAA, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project_manager_user = relationship("User", foreign_keys=[project_manager_id], back_populates="managed_projects")
    created_by_user = relationship("User", foreign_keys=[created_by_id], back_populates="created_projects")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    orders = relationship("Order", back_populates="project", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="project")