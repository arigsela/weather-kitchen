"""
RefreshToken model - stores hashed refresh tokens for revocation support.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import GUID
from app.models.base import DeclarativeBase


class RefreshToken(DeclarativeBase):
    """
    Stored refresh token (hashed).
    Enables revocation on logout and token rotation.
    """

    __tablename__ = "refresh_tokens"

    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)
    family_id = Column(GUID, ForeignKey("families.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    family = relationship("Family", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken family={self.family_id} revoked={self.revoked}>"
