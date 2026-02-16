"""
Family model - family account with authentication and COPPA compliance.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import DeclarativeBase, UUIDMixin, TimestampMixin
from app.database import GUID


class Family(DeclarativeBase):
    """
    Family entity - represents a family account.
    Includes API token hash for bearer authentication and PIN hash for sensitive operations.
    """

    __tablename__ = "families"
    __table_args__ = (
        Index("ix_families_api_token_hash", "api_token_hash", unique=True),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Core family data
    name = Column(String(100), nullable=False)
    family_size = Column(Integer, nullable=False)  # 1-20, used for recipe multiplier
    is_active = Column(Boolean, default=True, nullable=False)

    # API Token Authentication
    api_token_hash = Column(String(64), unique=True, nullable=False, index=True)
    token_created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # PIN Authentication (for sensitive operations)
    admin_pin_hash = Column(String(128), nullable=False)  # bcrypt hash
    pin_attempts = Column(Integer, default=0, nullable=False)
    pin_locked_until = Column(DateTime, nullable=True)  # Timestamp when lockout expires

    # COPPA Compliance
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)
    parent_email = Column(String(254), nullable=True)  # Email of parent/guardian

    # Consent Code (for email verification)
    consent_code_hash = Column(String(64), nullable=True)  # SHA256 hash of 6-digit code
    consent_code_expires_at = Column(DateTime, nullable=True)

    # GDPR Tracking
    has_minor_users = Column(Boolean, default=False, nullable=False)

    # Relationships
    users = relationship("User", back_populates="family", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="family", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<Family {self.name} (size={self.family_size}, active={self.is_active})>"
