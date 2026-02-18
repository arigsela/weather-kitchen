"""
Family model - family account with JWT authentication and PIN for sensitive operations.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import DeclarativeBase, UUIDMixin, TimestampMixin
from app.database import GUID


class Family(DeclarativeBase):
    """
    Family entity - represents a family account.
    Authenticates via JWT (access + refresh tokens).
    PIN hash used for sensitive operations (rotate, purge).
    """

    __tablename__ = "families"

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Core family data
    name = Column(String(100), nullable=False)
    family_size = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # PIN Authentication (for sensitive operations: rotate, purge)
    admin_pin_hash = Column(String(128), nullable=False)  # bcrypt hash
    pin_attempts = Column(Integer, default=0, nullable=False)
    pin_locked_until = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("User", back_populates="family", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="family", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="family", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<Family {self.name} (size={self.family_size}, active={self.is_active})>"
