"""
Refresh token repository - data access for JWT refresh tokens.
"""

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.jwt import hash_refresh_token
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Repository for RefreshToken entity."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, family_id: UUID, token: str, expires_at: datetime) -> RefreshToken:
        """Store a new hashed refresh token."""
        record = RefreshToken(
            id=uuid.uuid4(),
            family_id=family_id,
            token_hash=hash_refresh_token(token),
            expires_at=expires_at,
            revoked=False,
            created_at=datetime.now(UTC),
        )
        self.db.add(record)
        self.db.flush()
        return record

    def get_by_token(self, token: str) -> RefreshToken | None:
        """Lookup a refresh token record by plaintext token (hashed for lookup)."""
        token_hash = hash_refresh_token(token)
        return self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
        ).first()

    def revoke(self, token: str) -> bool:
        """Revoke a single refresh token. Returns True if found and revoked."""
        record = self.get_by_token(token)
        if not record:
            return False
        record.revoked = True
        self.db.add(record)
        self.db.flush()
        return True

    def revoke_all_for_family(self, family_id: UUID) -> int:
        """Revoke all active refresh tokens for a family. Returns count revoked."""
        records = self.db.query(RefreshToken).filter(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked == False,  # noqa: E712
        ).all()
        for record in records:
            record.revoked = True
        self.db.flush()
        return len(records)

    def cleanup_expired(self) -> int:
        """Delete expired and revoked tokens. Returns count deleted."""
        now = datetime.now(UTC)
        records = self.db.query(RefreshToken).filter(
            (RefreshToken.expires_at < now) | (RefreshToken.revoked == True)  # noqa: E712
        ).all()
        for record in records:
            self.db.delete(record)
        self.db.flush()
        return len(records)
