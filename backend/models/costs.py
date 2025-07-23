from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class CostBreakdown(Base):
    __tablename__ = "cost_breakdowns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Cost categories
    cost_type = Column(String(30), nullable=False)
    # Product Cost, Shipping, Insurance, Customs Duty, VAT
    # Handling Fee, Brokerage, Storage, Currency Conversion, Other

    # Cost details
    description = Column(String(200))
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(precision=10, scale=6))
    amount_in_base_currency = Column(Numeric(precision=12, scale=2))

    # Breakdown details
    rate_percentage = Column(Numeric(precision=5, scale=2))  # For percentage-based costs
    base_amount = Column(Numeric(precision=12, scale=2))  # Amount the percentage is applied to
    quantity = Column(Integer)
    unit_cost = Column(Numeric(precision=8, scale=2))

    # Status and approval
    status = Column(String(20), default="Estimated")  # Estimated, Confirmed, Invoiced, Paid
    is_budgeted = Column(Boolean, default=True)
    budget_variance = Column(Numeric(precision=12, scale=2))  # Actual - Budget

    # Payment tracking
    invoice_number = Column(String(100))
    invoice_date = Column(DateTime)
    payment_due_date = Column(DateTime)
    payment_date = Column(DateTime)
    payment_reference = Column(String(100))

    # Additional details
    vendor_name = Column(String(200))  # Who charged this cost
    cost_incurred_date = Column(DateTime)
    notes = Column(Text)

    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(100))
    approval_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    order = relationship("Order", back_populates="cost_breakdowns")