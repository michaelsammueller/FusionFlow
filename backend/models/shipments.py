from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Shipment identification
    tracking_number = Column(String(100), unique=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Shipment identification
    tracking_number = Column(String(100), unique=True, index=True)
    carrier = Column(String(100), nullable=False)  # DHL, FedEx, Aramex, etc.
    service_type = Column(String(50))  # Express, Standard, Economy, etc.
    carrier_reference = Column(String(100))  # Carrier's internal reference

    # Shipment type
    shipment_type = Column(String(20), default="Full")  # Full, Partial, Consolidated, Return
    is_partial_shipment = Column(Boolean, default=False)
    partial_shipment_number = Column(Integer, default=1)  # 1 of 3, 2 of 3, etc.

    # Origin information
    origin_address = Column(Text, nullable=False)
    origin_city = Column(String(100))
    origin_country = Column(String(100), nullable=False)
    origin_postal_code = Column(String(20))
    pickup_date = Column(DateTime)

    # Destination information
    destination_address = Column(Text, nullable=False)
    destination_city = Column(String(100))
    destination_country = Column(String(100), nullable=False)
    origin_postal_code = Column(String(20))

    # Timeline
    ship_date = Column(DateTime)
    estimated_delivery_date = Column(DateTime)
    promised_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)

    # Current status
    current_status = Column(String(30), default="Label Created")
    # Label Created, Picked Up, In Transit, Out for Delivery, Delivered,
    # Exception, Customs Delay, Returned, Lost

    current_location = Column(String(200))
    current_location_coordinates = Column(String(50))  # lat, lon
    last_status_update = Column(DateTime, default=datetime.utcnow)

    # Package details
    package_count = Column(Integer, default=1)
    total_weight_kg = Column(Numeric(precision=8, scale=3))
    total_volume_m3 = Column(Numeric(precision=8, scale=4))
    dimensions_cm = Column(String(50))  # "L x W x H"

    # Individual package details (JSON array)
    package_details = Column(JSON)  # [{"weight": 5.2, "dims": "30x20x15", "description": "Electronics"}]

    # Shipping costs
    shipping_cost = Column(Numeric(precision=10, scale=2))
    shipping_currency = Column(String(3), default="QAR")
    fuel_surcharge = Column(Numeric(precision=8, scale=2))
    handling_fee = Column(Numeric(precision=8, scale=2))
    insurance_cost = Column(Numeric(precision=8, scale=2))

    # Special handling
    is_dangerous_goods = Column(Boolean, default=False)
    dangerous_goods_class = Column(String(10))  # Class 1, Class 2, Class 3, etc.
    requires_signature = Column(Boolean, default=True)
    is_fragile = Column(Boolean, default=False)
    is_high_value = Column(Boolean, default=False)
    declared_value = Column(Numeric(precision=12, scale=2))

    # Temperature control (for sensitive equipment)
    requires_temperature_control = Column(Boolean, default=False)
    min_temperature_c = Column(Integer)
    max_temperature_c = Column(Integer)
    temperature_log = Column(JSON)  # Temperature readings during transit

    # Customs and international shipping
    is_international = Column(Boolean, default=False)
    customs_declaration_number = Column(String(100))
    commercial_invoice_value = Column(Numeric(precision=12, scale=2))
    harmonized_code = Column(String(20))
    country_of_origin = Column(String(100))

    # Delivery details
    delivery_to_name = Column(String(100))
    delivery_signature = Column(String(100))
    delivery_photo_path = Column(String(500))
    delivery_notes = Column(Text)
    proof_of_delivery_path = Column(String(500))

    # Quality check on receipt
    received_quantity = Column(Integer)
    condition_on_receipt = Column(String(20))  # Good, Damaged, Missing Parts, etc.
    damage_description = Column(Text)
    photos_on_receipt = Column(JSON)  # Array of photo paths
    received_by = Column(String(100))
    receipt_date = Column(DateTime)

    # Exception handling
    exception_reason = Column(String(200))
    exception_description = Column(Text)
    exception_resolution = Column(Text)
    exception_resolved_date = Column(DateTime)

    # API integration tracking
    last_api_sync = Column(DateTime)
    api_sync_frequency_minutes = Column(Integer, default=30)
    tracking_api_response = Column(JSON)  # {"status": "success", "message": "Tracking data updated"}

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="shipments")
    status_history = relationship("ShipmentStatusHistory", back_populates="shipment", cascade="all, delete-orphan")
    customs_entries = relationship("CustomsEntry", back_populates="shipment", cascade="all, delete-orphan")
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])

class ShipmentStatusHistory(Base):
    __tablename__ = "shipment_status_history"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    # Status change details
    status = Column(String(30), nullable=False)
    location = Column(String(200))
    location_coordinates = Column(String(50))  # lat, lon
    timestamp = Column(DateTime, nullable=False)

    # Additional details
    description = Column(Text)
    exception_code = Column(String(20))
    next_action = Column(String(200))

    # Source of update
    update_source = Column(String(20), default="API")  # API, Manual, System
    updated_by = Column(String(100))

    # Raw data from carrier API
    raw_api_data = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="status_history")