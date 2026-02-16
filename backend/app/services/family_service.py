"""
Family service - business logic for family operations.
"""

import hashlib
import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.family import Family
from app.repositories.family_repo import FamilyRepository
from app.auth.token import generate_api_token, hash_token as hash_api_token
from app.auth.pin import hash_pin, verify_pin as verify_pin_hash
from app.schemas.family import FamilyResponse, FamilyCreateResponse


class FamilyService:
    """Service layer for family operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FamilyRepository(db)

    def create_family(
        self,
        name: str,
        family_size: int,
        admin_pin: str,
    ) -> tuple[FamilyResponse, str]:
        """
        Create new family account.

        Args:
            name: Family name
            family_size: Number of family members
            admin_pin: 4-6 digit numeric PIN

        Returns:
            Tuple of (family response, plaintext token)
        """
        # Generate API token (return plaintext + hash)
        plaintext_token, token_hash = generate_api_token()

        # Hash PIN
        pin_hash = hash_pin(admin_pin)

        # Create family
        family = self.repository.create_family(
            name=name,
            family_size=family_size,
            api_token_hash=token_hash,
            admin_pin_hash=pin_hash,
        )

        self.db.commit()

        response = FamilyResponse.model_validate(family)
        return response, plaintext_token

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

    def rotate_token(self, family_id: UUID) -> Optional[str]:
        """
        Rotate API token (generate new token, invalidate old).

        Args:
            family_id: Family ID

        Returns:
            New plaintext token or None if family not found
        """
        plaintext_token, new_token_hash = generate_api_token()

        family = self.repository.update_token_hash(family_id, new_token_hash)
        if not family:
            return None

        self.db.commit()
        return plaintext_token

    def verify_pin(self, family_id: UUID, admin_pin: str) -> tuple[bool, Optional[str]]:
        """
        Verify PIN and handle lockout/attempt tracking.

        Args:
            family_id: Family ID
            admin_pin: PIN to verify

        Returns:
            Tuple of (success: bool, lockout_message: str or None)
        """
        family = self.repository.get_by_id(family_id)
        if not family:
            return False, "Family not found"

        # Check lockout (handle both naive and aware datetimes from SQLite)
        if family.pin_locked_until:
            locked_until = family.pin_locked_until
            # Make aware if naive (SQLite doesn't store timezone)
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > datetime.now(timezone.utc):
                return False, f"Locked until {locked_until.isoformat()}"

        # Verify PIN
        pin_correct = verify_pin_hash(admin_pin, family.admin_pin_hash)

        if not pin_correct:
            # Increment attempts
            self.repository.update_pin_attempts(family_id, family.pin_attempts + 1)
            self.db.commit()
            remaining = max(0, 5 - (family.pin_attempts + 1))
            return False, f"Invalid PIN ({remaining} attempts remaining)"

        # PIN correct - reset attempts
        self.repository.reset_pin_attempts(family_id)
        self.db.commit()
        return True, None

    def request_consent_code(self, family_id: UUID) -> Optional[str]:
        """
        Generate and store consent verification code.

        Args:
            family_id: Family ID

        Returns:
            6-digit code or None if family not found
        """
        family = self.repository.get_by_id(family_id)
        if not family:
            return None

        # Generate 6-digit code
        code = secrets.randbelow(999999)
        code_str = f"{code:06d}"

        # Hash code
        code_hash = hashlib.sha256(code_str.encode()).hexdigest()

        # Store in family
        self.repository.set_consent_code(family_id, code_hash, expires_in_minutes=24*60)
        self.db.commit()

        return code_str

    def verify_consent_code(self, family_id: UUID, code: str) -> bool:
        """
        Verify consent code and set consent if valid.

        Args:
            family_id: Family ID
            code: 6-digit code to verify

        Returns:
            True if code valid and consent set, False otherwise
        """
        family = self.repository.get_by_id(family_id)
        if not family or not family.consent_code_hash:
            return False

        # Check expiry (handle both naive and aware datetimes from SQLite)
        if family.consent_code_expires_at:
            expires_at = family.consent_code_expires_at
            # Make aware if naive (SQLite doesn't store timezone)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                self.repository.clear_consent_code(family_id)
                self.db.commit()
                return False

        # Verify code
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash != family.consent_code_hash:
            return False

        # Set consent
        self.repository.set_consent(family_id, True)
        self.repository.clear_consent_code(family_id)
        self.db.commit()
        return True

    def export_family_data(self, family_id: UUID) -> Optional[dict]:
        """Export all family data for GDPR compliance."""
        family = self.repository.get_by_id(family_id, include_inactive=True)
        if not family:
            return None

        # Get all users
        users = self.db.query(Family).filter(Family.id == family_id).first()
        if not users:
            users = []
        else:
            users = [{"id": str(u.id), "name": u.name} for u in users.users] if users.users else []

        # Get audit log
        audit_log = []  # TODO: Implement when AuditLog service exists

        return {
            "family": FamilyResponse.model_validate(family).model_dump(),
            "users": users,
            "audit_log": audit_log,
            "export_date": datetime.now(timezone.utc).isoformat(),
        }
