from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from backend.database import Base
from datetime import datetime

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Setting identification
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_category = Column(String(50), nullable=False)  # Email, API, Notifications, Currency, etc.

    # Setting values
    string_value = Column(String(500))
    integer_value = Column(Integer)
    boolean_value = Column(Boolean)
    json_value = Column(JSON)
    text_value = Column(Text)

    # Settings metadata
    display_name = Column(String(200))
    description = Column(Text)
    data_type = Column(String(20))  # string, integer, boolean, json, text
    is_encrypted = Column(Boolean, default=False)

    # Access control
    is_user_configurable = Column(Boolean, default=True)
    required_role = Column(String(20))  # admin, manager, user

    # Validation
    validation_rules = Column(JSON)  # Store validation constraints
    default_value = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100))