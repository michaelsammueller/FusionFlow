from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))

    # Notification details
    notification_type = Column(String(30), nullable=False)
    # Order Status Change, Delivery Delay, Customs Issue, Payment Due,
    # Document Required, Quality Issue, Supplier Update, System Alert

    priority = Column(String(10), default="Normal")  # Low, Normal, High, Critical

    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    action_required = Column(Boolean, default=False)
    action_url = Column(String(500))  # Link to relevant page/form
    action_button_text = Column(String(50))  # "View Order", "Approve Payment", etc.

    # Related entities (for navigation and filtering)
    related_order_id = Column(Integer)
    related_supplier_id = Column(Integer)
    related_shipment_id = Column(Integer)

    # Delivery channels
    sent_via_email = Column(Boolean, default=False)
    sent_via_sms = Column(Boolean, default=False)
    sent_via_app = Column(Boolean, default=True)

    # Email details
    email_sent_at = Column(DateTime)
    email_delivery_status = Column(String(20))  # Sent, Delivered, Failed, Bounced

    # SMS details
    sms_sent_at = Column(DateTime)
    sms_delivery_status = Column(String(20))

    # Status tracking
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime)

    # Escalation
    escalation_level = Column(Integer, default=0)  # 0=normal, 1=first escalation, etc.
    escalated_to_user_id = Column(Integer, ForeignKey("users.id"))
    escalation_date = Column(DateTime)

    # Auto-generated vs manual
    is_auto_generated = Column(Boolean, default=True)
    created_by_system = Column(String(50))  # "Order Monitor", "Carrier API", "Manual"

    # Grouping and batching
    notification_group = Column(String(100))  # Group related notifications
    batch_id = Column(String(50))  # For batch notifications

    # Additional data
    meta_data = Column(JSON)  # Store additional context data

    # Scheduling
    scheduled_send_time = Column(DateTime)  # For delayed notifications
    expires_at = Column(DateTime)  # Auto-archive after this time

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    escalated_to_user = relationship(
        "User",
        foreign_keys=[escalated_to_user_id],
        back_populates="escalated_notifications"
    )
    project = relationship("Project", back_populates="notifications")