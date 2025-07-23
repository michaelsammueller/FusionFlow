from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(Strings(50), unique=True, nullable=False, index=True)
    po_number = Column(String(50), index=True)  # Purchase Order Number
    rfq_number = Column(String(50))  # Request for Quote reference

    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Order details
    description = Column(Text, nullable=False)
    part_number = Column(String(100))
    manufacturer_part_number = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_of_measure = Column(String(20), default="pcs")  # pcs, kg, m, etc.
    
    # Pricing
    unit_price = Column(Numeric(precision=12, scale=4), nullable=False)
    total_amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String(3), default="QAR")
    exchange_rate_to_base = Column(Numeric(precision=10, scale=6), default=1.0)

    # Important dates
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    requested_delivery_date = Column(DateTime, nullable=False)
    promised_delivery_date = Column(DateTime)  # Supplier's commitment
    actual_delivery_date = Column(DateTime)

    # Status tracking
    status = Column(String(20), default="Draft")
    # Draft, Pending Approval, Approved, Sent to Supplier, Confirmed
    # In Production, Ready to Ship, Shipped, In Transit, Customs
    # Out for Delivery, Delivered, Partially Delivered, Cancelled, On Hold
    # Rejected, Returned, Invoiced, Paid, Closed

    previous_status = Column(String(20))  # For status change tracking
    status_changed_at = Column(DateTime)
    status_changed_by = Column(String(100))

    # Priority and criticality
    priority = Column(String(10), default="Normal")  # Low, Normal, High, Critical
    is_critical_path = Column(Boolean, default=False)
    is_long_lead_time = Column(Boolean, default=False)
    criticality_reason = Column(Text)

    # Delivery information
    delivery_address = Column(Text)
    delivery_contact_person = Column(String(100))
    delivery_contact_phone = Column(String(50))
    special_delivery_instructions = Column(Text)

    # Shipping details
    shipping_method = Column(String(50))  # Air, Sea, Road, Rail
    incoterms = Column(String(10))  # EXW, FOB, CIF, DDP, etc.
    tracking_number = Column(String(100))
    estimated_transit_days = Column(Integer)

    # Compliance and certification
    requires_certification = Column(Boolean, default=False)
    certification_type = Column(String(100))  # EASA, QCAA, ICAO, MOI, Military
    certificate_number = Column(String(100))
    certificate_received = Column(Boolean, default=False)
    certificate_expiry_date = Column(DateTime)

    # Quality and traceability
    requires_mil_standard = Column(Boolean, default=False)
    mil_standard_number = Column(String(50))
    serial_numbers = Column(JSON)  # ["123456", "789012"]
    batch_lot_numbers = Column(JSON)
    manufacturing_date = Column(DateTime)
    shelf_life_months = Column(Integer)
    expiry_date = Column(DateTime)

    # Financial tracking
    advance_payment_required = Column(Boolean, default=False)
    advance_payment_percentage = Column(Numeric(precision=5, scale=2))
    advance_payment_amount = Column(Numeric(precision=15, scale=2))
    advance_payment_status = Column(String(20), default="Not Required")
    # Not Required, Required, Requested, Approved, Paid

    payment_terms = Column(String(100))
    payment_status = Column(String(20), default="Pending")
    # Pending, Advance Paid, Full Payment Due, Paid, Overdue

    # Budget and cost tracking
    budgeted_amount = Column(Numeric(precision=15, scale=2))
    budget_variance = Column(Numeric(precision=15, scale=2))  # Actual vs Budget

    # Lead time tracking
    quoted_lead_time_days = Column(Integer)
    actual_lead_time_days = Column(Integer)  # Calculated when delivered
    lead_time_variance_days = Column(Integer)  # Actual - Quoted

    # Risk Management
    risk_level = Column(String(10), default="Low")  # Low, Medium, High
    risk_factors = Column(JSON)  # ["Single Source", "Long Lead Time", "Complex Logistics"]
    mitigation_actions = Column(Text)

    # Communication tracking
    last_supplier_communication = Column(DateTime)
    supplier_response_time_hours = Column(Integer)
    communication_quality_rating = Column(Integer)  # 1-5 scale

    # Internal notes and approvals
    internal_notes = Column(Text)
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="orders")
    supplier = relationship("Supplier", back_populates="orders")
    created_by_user = relationship("User", back_populates="created_orders")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="order", cascade="all, delete-orphan")
    cost_breakdown = relationship("CostBreakdown", back_populates="order", cascade="all, delete-orphan")
    custom_entries = relationship("CustomsEntry", back_populates="order", cascade="all, delete-orphan")