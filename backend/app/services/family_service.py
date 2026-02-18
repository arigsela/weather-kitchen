"""
Family service - business logic for family operations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.pin import hash_pin, verify_pin as verify_pin_hash
from app.config import settings
from app.models.family import Family
from app.repositories.family_repo import FamilyRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.schemas.family import FamilyResponse


class FamilyService:
    """Service layer for family operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FamilyRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)

    def create_family(
        self,
        name: str,
        family_size: int,
        admin_pin: str,
    ) -> tuple[FamilyResponse, str, str]:
        """
        Create new family account and issue JWT token pair.

        Returns:
            Tuple of (family_response, access_token, refresh_token)
        """
        pin_hash = hash_pin(admin_pin)

        family = self.repository.create_family(
            name=name,
            family_size=family_size,
            admin_pin_hash=pin_hash,
        )
        self.db.flush()

        # Issue JWT tokens
        access_token = create_access_token(str(family.id))
        refresh_token, _ = create_refresh_token(str(family.id))

        # Persist refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        self.refresh_repo.create(family.id, refresh_token, expires_at)

        self.db.commit()

        response = FamilyResponse.model_validate(family)
        return response, access_token, refresh_token

    def get_family(self, family_id: UUID) -> Optional[FamilyResponse]:
        """Get family by ID."""
        family = self.repository.get_by_id(family_id)
        if not family:
            return None
        return FamilyResponse.model_validate(family)

    def update_family(
        self,
        family_id: UUID,
        name: Optional[str] = None,
        family_size: Optional[int] = None,
    ) -> Optional[FamilyResponse]:
        """Update family settings."""
        family = self.repository.get_by_id(family_id)
        if not family:
            return None

        if name is not None:
            family.name = name
        if family_size is not None:
            family.family_size = family_size

        family.updated_at = datetime.now(timezone.utc)
        self.db.add(family)
        self.db.commit()

        return FamilyResponse.model_validate(family)

    def soft_delete(self, family_id: UUID) -> bool:
        """Soft delete family (mark as inactive)."""
        success = self.repository.soft_delete(family_id)
        if success:
            self.db.commit()
        return success

    def hard_delete(self, family_id: UUID) -> bool:
        """Hard delete family (permanent, requires PIN verification)."""
        success = self.repository.hard_delete(family_id)
        if success:
            self.db.commit()
        return success

    def rotate_tokens(self, family_id: UUID) -> tuple[str, str]:
        """
        Revoke all existing refresh tokens and issue a new JWT pair.
        PIN verification must be done by the caller before calling this.

        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Revoke all existing refresh tokens for this family
        self.refresh_repo.revoke_all_for_family(family_id)

        # Issue new pair
        access_token = create_access_token(str(family_id))
        refresh_token, _ = create_refresh_token(str(family_id))

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        self.refresh_repo.create(family_id, refresh_token, expires_at)

        self.db.commit()
        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> Optional[tuple[str, str]]:
        """
        Validate a refresh token and issue a new access + refresh pair (rotation).

        Returns:
            Tuple of (new_access_token, new_refresh_token) or None if invalid
        """
        import jwt as pyjwt
        from app.auth.jwt import decode_token

        # Decode JWT claims first
        try:
            payload = decode_token(refresh_token)
        except pyjwt.InvalidTokenError:
            return None

        if payload.get("type") != "refresh":
            return None

        family_id = payload.get("sub")
        if not family_id:
            return None

        # Check DB record: must exist, not revoked, not expired
        record = self.refresh_repo.get_by_token(refresh_token)
        if not record or record.revoked:
            return None

        now = datetime.now(timezone.utc)
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            return None

        # Revoke old refresh token (rotation)
        record.revoked = True
        self.db.add(record)

        # Issue new pair
        new_access = create_access_token(family_id)
        new_refresh, _ = create_refresh_token(family_id)

        new_expires_at = now + timedelta(days=settings.jwt_refresh_token_expire_days)
        self.refresh_repo.create(family_id, new_refresh, new_expires_at)

        self.db.commit()
        return new_access, new_refresh

    def logout(self, refresh_token: str) -> bool:
        """Revoke a refresh token (logout)."""
        revoked = self.refresh_repo.revoke(refresh_token)
        if revoked:
            self.db.commit()
        return revoked

    def verify_pin(self, family_id: UUID, admin_pin: str) -> tuple[bool, Optional[str]]:
        """
        Verify PIN and handle lockout/attempt tracking.

        Returns:
            Tuple of (success: bool, error_message: str | None)
        """
        family = self.repository.get_by_id(family_id)
        if not family:
            return False, "Family not found"

        if family.pin_locked_until:
            locked_until = family.pin_locked_until
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > datetime.now(timezone.utc):
                return False, f"Locked until {locked_until.isoformat()}"

        pin_correct = verify_pin_hash(admin_pin, family.admin_pin_hash)

        if not pin_correct:
            self.repository.update_pin_attempts(family_id, family.pin_attempts + 1)
            self.db.commit()
            remaining = max(0, 5 - (family.pin_attempts + 1))
            return False, f"Invalid PIN ({remaining} attempts remaining)"

        self.repository.reset_pin_attempts(family_id)
        self.db.commit()
        return True, None

    def export_family_data(self, family_id: UUID) -> Optional[dict]:
        """Export all family data for GDPR compliance."""
        family = self.repository.get_by_id(family_id, include_inactive=True)
        if not family:
            return None

        users = [{"id": str(u.id), "name": u.name} for u in family.users] if family.users else []
        audit_log = []

        return {
            "family": FamilyResponse.model_validate(family).model_dump(),
            "users": users,
            "audit_log": audit_log,
            "export_date": datetime.now(timezone.utc).isoformat(),
        }
