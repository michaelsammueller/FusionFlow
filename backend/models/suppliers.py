from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)

    # Contact information
    primary_contact_person = Column(String(100))
    primary_email = Column(String(255))
    primary_phone = Column(String(50))
    secondary_contact_person = Column(String(100))
    secondary_email = Column(String(255))
    secondary_phone = Column(String(50))

    # Address information
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))

    # Business information
    company_registration_number = Column(String(100))
    tax_id = Column(String(100))
    website = Column(String(255))

    # Capabilities and certifications
    is_local_company = Column(Boolean, default=False)
    certifications = Column(JSON)  # Store as JSON array of strings
    product_categories = Column(JSON)  # ["Electronics", "Mechanical", "Software"]
    geographical_coverage = Column(JSON)  # Countries/regions they can ship to

    # Performance metrics (calculated fields)
    total_orders_count = Column(Integer, default=0)
    total_order_value = Column(Numeric(precision=15, scale=2), default=0)
    on_time_deliveries = Column(Integer, default=0)
    late_deliveries = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)

    # Calculated performance scores (updated by background jobs)
    on_time_delivery_rate = Column(Numeric(precision=5, scale=2), default=0)  # Percentage
    average_lead_time_days = Column(Integer, default=0)
    quality_rating = Column(Numeric(precision=3, scale=2), default=0)  # 1.00 to 5.00
    communication_rating = Column(Numeric(precision=3, scale=2), default=0)
    cost_competitiveness_rating = Column(Numeric(precision=3, scale=2), default=0)
    overall_performance_score = Column(Numeric(precision=3, scale=2), default=0)

    # Financial terms
    payment_terms = Column(String(100))  # "30 days", "Advance payment", "LC"
    currency_preference = Column(String(3), default="QAR")
    credit_limit = Column(Numeric(precision=15, scale=2))

    # Shipping preferences
    preferred_shipping_methods = Column(JSON)  # ["DHL Express", "FedEx", "Aramex", "Sea Freight"]
    can_handle_dangerous_goods = Column(Boolean, default=False)
    can_handle_oversized_items = Column(Boolean, default=False)

    # Status and approval
    approval_status = Column(String(20), default="Pending")  # Pending, Approved, Suspended, Rejected, Blacklisted
    approved_by = Column(String(100))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)

    # Relationship management
    account_manager = Column(String(100))  # Internal person managing this supplier
    last_communication_date = Column(DateTime)
    next_review_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    orders = relationship("Order", back_populates="supplier")
    performance_records = relationship("SupplierPerformance", back_populates="supplier", cascade="all, delete-orphan")