from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class CustomsEntry(Base):
    __tablename__ = "customs_entries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))

    # Customs identification
    customs_reference_number = Column(String(100), unique=True, index=True)
    entry_type = Column(String(20))  # Import, Export, Transit, Temporary
    customs_office = Column(String(200))

    # Customs status
    status = Column(String(30), default="Pending")
    # Pending, Submitted, Under Review, Inspection Required
    # Additional Document Required, Cleared, Rejected, Appeal

    status_updated_at = Column(DateTime, default=datetime.utcnow)

    # Import/Export details
    port_of_entry = Column(String(200))
    port_of_exit = Column(String(200))
    vessel_flight_number = Column(String(50))

    # Financial details
    declared_value = Column(Numeric(precision=15, scale=2))
    declared_currency = Column(String(3))
    duty_rate_percentage = Column(Numeric(precision=5, scale=2))
    duty_amount = Column(Numeric(precision=12, scale=2))
    vat_rate_percentage = Column(Numeric(precision=5, scale=2))
    vat_amount = Column(Numeric(precision=12, scale=2))
    other_fees = Column(Numeric(precision=12, scale=2))
    total_charges = Column(Numeric(precision=12, scale=2))

    # Payment details
    payment_status = Column(String(20), default="Pending")  # Pending, Paid, Overdue
    payment_due_date = Column(DateTime)
    payment_date = Column(DateTime)
    payment_reference = Column(String(100))

    # Classification
    harmonized_code = Column(String(20))
    country_of_origin = Column(String(100))
    product_description = Column(Text)

    # Temporary import (for demo equipment)
    is_temporary_import = Column(Boolean, default=False)
    temporary_import_permit_number = Column(String(100))
    temporary_import_expiry_date = Column(DateTime)
    carnet_number = Column(String(100))  # ATA Carnet for temporary imports

    # Documentation 
    commercial_invoice_number = Column(String(100))
    packing_list_available = Column(Boolean, default=False)
    certificate_of_origin_available = Column(Boolean, default=False)

    # Inspection details
    inspection_required = Column(Boolean, default=False)
    inspection_scheduled_date = Column(DateTime)
    inspection_completed_date = Column(DateTime)
    inspection_result = Column(String(20))  # Passed, Failed, Conditional
    inspection_notes = Column(Text)

    # Additional requirements
    requires_import_license = Column(Boolean, default=False)
    import_license_number = Column(String(100))
    requires_special_permits = Column(Boolean, default=False)
    special_permit_details = Column(JSON)

    # Broker information
    customs_broker_name = Column(String(200))
    customs_broker_license = Column(String(100))
    customs_broker_contact = Column(String(100))

    # Additional nontes and communication
    customs_notes = Column(Text)
    communication_log = Column(JSON)  # Track all communications with customs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    order = relationship("Order", back_populates="customs_entries")
    shipment = relationship("Shipment", back_populates="customs_entries")
    
    