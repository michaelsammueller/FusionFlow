from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(100), nullable=False)

    # Role-based access
    role = Column(String(50), default="user")  # admin, manager, procurement, field, qa, finance
    department = Column(String(50))  # Management, Procurement, Field Operations, QA, Finance

    # User preferences
    timezone = Column(String(50), default="Asia/Doha")
    language = Column(String(5), default="en")  # en, ar
    notification_preferences = Column(Text)  # JSON string

    # Status tracking
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))

    # Relationships
    created_projects = relationship("Project", foreign_keys="Project.created_by_id", back_populates="created_by_user")
    managed_projects = relationship("Project", foreign_keys="Project.project_manager_id", back_populates="project_manager_user")
    created_orders = relationship("Order", back_populates="created_by_user")
    notifications = relationship("Notification", back_populates="user")
