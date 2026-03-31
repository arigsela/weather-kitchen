"""
Family model - family account with JWT authentication and PIN for sensitive operations.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import GUID
from app.models.base import DeclarativeBase, TimestampMixin


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

    # Password Authentication (for login and sensitive operations)
    password_hash = Column(String(128), nullable=True)  # bcrypt hash

    # PIN Authentication (legacy, kept for backward compat)
    admin_pin_hash = Column(String(128), nullable=True)  # bcrypt hash
    pin_attempts = Column(Integer, default=0, nullable=False)
    pin_locked_until = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("User", back_populates="family", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="family", cascade="all, delete-orphan")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="family", cascade="all, delete-orphan"
    )

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<Family {self.name} (size={self.family_size}, active={self.is_active})>"
