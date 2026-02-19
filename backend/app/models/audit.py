"""
AuditLog model for tracking all state-changing operations.
Used for GDPR compliance, debugging, and security auditing.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.database import GUID
from app.models.base import DeclarativeBase


class AuditLog(DeclarativeBase):
    """
    Audit log entry - immutable record of state-changing operations.
    Records: who (user), what (action), when (timestamp), where (IP), details (JSON).
    """

    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_family_id", "family_id"),)

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Context
    family_id = Column(GUID, ForeignKey("families.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(GUID, nullable=True)

    # Action details
    action = Column(
        String(100), nullable=False
    )  # e.g., "token.rotated", "pin.failed", "family.deleted"
    entity_type = Column(String(50), nullable=False)  # e.g., "recipe", "user", "family"
    entity_id = Column(GUID, nullable=False)

    # Request context
    ip = Column(String(45), nullable=False)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)

    # Additional details (JSON)
    details = Column(Text, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=False)

    # Relationship
    family = relationship("Family", back_populates="audit_logs")

    def __repr__(self):
        return (
            f"<AuditLog {self.action} on {self.entity_type}({self.entity_id}) at {self.timestamp}>"
        )
