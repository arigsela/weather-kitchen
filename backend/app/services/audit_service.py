"""
Audit logging service - records all state-changing operations for GDPR compliance,
security auditing, and debugging. All writes happen asynchronously via BackgroundTasks
to avoid adding latency to the critical request path.
"""

import uuid
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.audit import AuditLog


class AuditService:
    """Service layer for audit log operations."""

    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        family_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID,
        ip: str,
        user_agent: str | None = None,
        user_id: UUID | None = None,
        details: str | None = None,
    ) -> AuditLog:
        """
        Create an audit log entry for a state-changing operation.

        Args:
            family_id: Family context for the action (may be None for pre-auth events)
            action: Dot-namespaced action label e.g. "token.rotated", "pin.failed"
            entity_type: Affected resource type e.g. "family", "user", "auth"
            entity_id: UUID of the affected entity
            ip: Originating IP address (IPv4 or IPv6, max 45 chars)
            user_agent: HTTP User-Agent header value (optional)
            user_id: User performing the action within the family (optional)
            details: Pre-serialised JSON string with supplementary data (optional)

        Returns:
            The persisted AuditLog instance
        """
        entry = AuditLog(
            id=uuid.uuid4(),
            family_id=family_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip=ip,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.now(UTC),
        )
        self.db.add(entry)
        self.db.commit()
        return entry

    def log_auth_event(
        self,
        family_id: UUID | None,
        action: str,
        ip: str,
        user_agent: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        """
        Convenience wrapper for authentication-related events.

        Sets entity_type="auth" and entity_id=family_id so callers do not
        have to repeat the auth-specific entity boilerplate.

        Args:
            family_id: Family context; also used as the entity_id
            action: Auth action label e.g. "pin.failed", "token.rotated"
            ip: Originating IP address
            user_agent: HTTP User-Agent header value (optional)
            details: Pre-serialised JSON string with supplementary data (optional)

        Returns:
            The persisted AuditLog instance
        """
        entity_id = family_id if family_id is not None else uuid.uuid4()
        return self.log_action(
            family_id=family_id,
            action=action,
            entity_type="auth",
            entity_id=entity_id,
            ip=ip,
            user_agent=user_agent,
            details=details,
        )

    def get_logs_for_family(
        self,
        family_id: UUID,
        limit: int = 50,
    ) -> list[AuditLog]:
        """
        Return the most recent audit log entries for a family.

        Args:
            family_id: Family whose log entries to retrieve
            limit: Maximum number of entries to return (default 50)

        Returns:
            List of AuditLog instances ordered newest-first
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.family_id == family_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        Hard-delete audit log entries older than retention_days.

        Intended to be called from a scheduled nightly task.  The 90-day
        default aligns with the GDPR retention policy defined in the PRD.

        Args:
            retention_days: Number of days to retain logs (default 90)

        Returns:
            Number of rows deleted
        """
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        deleted = (
            self.db.query(AuditLog)
            .filter(AuditLog.timestamp < cutoff)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted


# ---------------------------------------------------------------------------
# Background-task helper
# ---------------------------------------------------------------------------


def _audit_log_background(
    action: str,
    entity_type: str,
    entity_id: UUID,
    ip: str,
    family_id: UUID | None = None,
    user_id: UUID | None = None,
    user_agent: str | None = None,
    details: str | None = None,
) -> None:
    """
    Synchronous helper executed via BackgroundTasks.add_task().

    Opens its own database session so it runs independently of the
    request-scoped session that has already been closed by the time
    BackgroundTasks executes.

    Args:
        action: Dot-namespaced action label
        entity_type: Affected resource type
        entity_id: UUID of the affected entity
        ip: Originating IP address
        family_id: Family context (optional)
        user_id: Acting user within the family (optional)
        user_agent: HTTP User-Agent header value (optional)
        details: Pre-serialised JSON string (optional)
    """
    db = SessionLocal()
    try:
        AuditService(db).log_action(
            family_id=family_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip=ip,
            user_agent=user_agent,
            user_id=user_id,
            details=details,
        )
    except Exception:
        # Audit failures must never crash the request or its background tasks.
        # Errors are intentionally swallowed here; the request has already
        # completed successfully from the client's perspective.
        db.rollback()
    finally:
        db.close()
