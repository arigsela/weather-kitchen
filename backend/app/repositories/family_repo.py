"""
Family repository - data access layer for family operations.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.family import Family
from app.repositories.base import BaseRepository


class FamilyRepository(BaseRepository[Family]):
    """Repository for Family entity."""

    def __init__(self, db: Session):
        super().__init__(db, Family)

    def get_by_token_hash(self, token_hash: str) -> Optional[Family]:
        """Get family by API token hash."""
        return self.db.query(Family).filter(Family.api_token_hash == token_hash).first()

    def get_by_id(self, family_id: UUID, include_inactive: bool = False) -> Optional[Family]:
        """Get family by ID."""
        query = self.db.query(Family).filter(Family.id == family_id)
        if not include_inactive:
            query = query.filter(Family.is_active == True)
        return query.first()

    def create_family(
        self,
        name: str,
        family_size: int,
        api_token_hash: str,
        admin_pin_hash: str,
    ) -> Family:
        """Create new family account."""
        family = Family(
            id=self._generate_uuid(),
            name=name,
            family_size=family_size,
            api_token_hash=api_token_hash,
            admin_pin_hash=admin_pin_hash,
            token_created_at=datetime.now(timezone.utc),
            is_active=True,
            consent_given=False,
            has_minor_users=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(family)
        self.db.flush()
        return family

    def update_token_hash(self, family_id: UUID, new_token_hash: str) -> Optional[Family]:
        """Update API token hash (for token rotation)."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.api_token_hash = new_token_hash
        family.token_created_at = datetime.now(timezone.utc)
        family.updated_at = datetime.now(timezone.utc)
        self.db.add(family)
        self.db.flush()
        return family

    def update_pin_attempts(self, family_id: UUID, attempts: int) -> Optional[Family]:
        """Update PIN attempt count."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.pin_attempts = attempts
        if attempts >= 5:
            family.pin_locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        else:
            family.pin_locked_until = None

        self.db.add(family)
        self.db.flush()
        return family

    def reset_pin_attempts(self, family_id: UUID) -> Optional[Family]:
        """Reset PIN attempts after successful verification."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.pin_attempts = 0
        family.pin_locked_until = None
        self.db.add(family)
        self.db.flush()
        return family

    def soft_delete(self, family_id: UUID) -> bool:
        """Soft delete family (mark as inactive)."""
        family = self.get_by_id(family_id, include_inactive=True)
        if not family:
            return False

        family.is_active = False
        family.updated_at = datetime.now(timezone.utc)
        self.db.add(family)
        self.db.flush()
        return True

    def hard_delete(self, family_id: UUID) -> bool:
        """Hard delete family (permanent deletion)."""
        family = self.get_by_id(family_id, include_inactive=True)
        if not family:
            return False

        self.db.delete(family)
        self.db.flush()
        return True

    def set_consent(self, family_id: UUID, consent_given: bool) -> Optional[Family]:
        """Update COPPA consent status."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.consent_given = consent_given
        if consent_given:
            family.consent_date = datetime.now(timezone.utc)
        family.updated_at = datetime.now(timezone.utc)
        self.db.add(family)
        self.db.flush()
        return family

    def set_consent_code(
        self,
        family_id: UUID,
        consent_code_hash: str,
        expires_in_minutes: int = 24 * 60,
    ) -> Optional[Family]:
        """Set consent verification code and expiry."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.consent_code_hash = consent_code_hash
        family.consent_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        self.db.add(family)
        self.db.flush()
        return family

    def clear_consent_code(self, family_id: UUID) -> Optional[Family]:
        """Clear consent code after verification."""
        family = self.get_by_id(family_id)
        if not family:
            return None

        family.consent_code_hash = None
        family.consent_code_expires_at = None
        self.db.add(family)
        self.db.flush()
        return family

    def has_minor_users(self, family_id: UUID) -> bool:
        """Check if family has minor users."""
        family = self.get_by_id(family_id)
        if not family:
            return False

        return family.has_minor_users

    def _generate_uuid(self):
        """Generate a new UUID."""
        import uuid
        return uuid.uuid4()

    def get_soft_deleted_before(self, cutoff_date: datetime) -> list[Family]:
        """Get families soft-deleted before cutoff date."""
        return self.db.query(Family).filter(
            Family.is_active == False,
            Family.updated_at <= cutoff_date,
        ).all()
