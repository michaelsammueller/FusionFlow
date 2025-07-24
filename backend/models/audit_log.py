from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from backend.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who did what
    user_id = Column(Integer)  # Can be null for system actions
    username = Column(String(100))
    user_role = Column(String(20))

    # What happened
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    entity_type = Column(String(50), nullable=False)  # Order, Project, Supplier, etc.
    entity_id = Column(Integer)

    # Details
    description = Column(String(500))
    old_values = Column(JSON)  # Before state
    new_values = Column(JSON)  # After state

    # Context
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    session_id = Column(String(100))

    # System info
    system_source = Column(String(50))  # Web UI, API, Background Job, etc.
    correlation_id = Column(String(100))  # For tracking related actions

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Additional metadata
    meta_data = Column(JSON)

    level = Column(String(20), default="info")  # info, warning, critical, etc.