"""
FastAPI dependency injection for authentication and authorization.
"""

import hashlib
from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.family import Family
from app.auth.pin import verify_pin as verify_pin_hash, check_lockout


def get_token_from_header(authorization: str | None) -> str:
    """Extract bearer token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format (expected: Bearer <token>)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return parts[1]


def hash_token(token: str) -> str:
    """Hash token for database lookup."""
    return hashlib.sha256(token.encode()).hexdigest()


async def get_current_family(
    authorization: str | None = None,
    db: Session = Depends(get_db),
) -> Family:
    """
    Verify Bearer token and return the authenticated family.

    Args:
        authorization: Authorization header
        db: Database session

    Returns:
        Family object

    Raises:
        HTTPException 401 if token missing or invalid
        HTTPException 404 if family not found (prevents enumeration)
    """
    token = get_token_from_header(authorization)
    token_hash = hash_token(token)

    # Look up family by token hash
    family = db.query(Family).filter(Family.api_token_hash == token_hash).first()

    if not family or not family.is_active:
        # Return 404 instead of 401 to prevent token enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found or inactive",
        )

    return family


async def require_family_owner(
    family_id: UUID,
    current_family: Family = Depends(get_current_family),
) -> Family:
    """
    Verify that the authenticated family ID matches the requested family ID.

    Args:
        family_id: Family ID from URL path
        current_family: Currently authenticated family

    Returns:
        Family object if owner matches

    Raises:
        HTTPException 404 if family IDs don't match (prevents enumeration)
    """
    if current_family.id != family_id:
        # Return 404 instead of 403 to prevent family enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found or access denied",
        )

    return current_family


async def require_pin(
    pin: str,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> Family:
    """
    Verify PIN and check lockout status.

    Args:
        pin: PIN to verify
        family: Currently authenticated family
        db: Database session

    Returns:
        Family object if PIN is correct

    Raises:
        HTTPException 423 if family is locked out
        HTTPException 403 if PIN is incorrect
    """
    # Check lockout status
    is_locked, lockout_expires_at = check_lockout(
        family.pin_attempts,
        family.pin_locked_until,
    )

    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Too many failed attempts. Try again after {lockout_expires_at}",
        )

    # Verify PIN
    pin_correct = verify_pin_hash(pin, family.admin_pin_hash)

    if not pin_correct:
        # Increment failed attempts
        family.pin_attempts += 1

        # Check if we should lock out
        if family.pin_attempts >= 5:  # PIN_MAX_ATTEMPTS from config
            from datetime import timedelta
            family.pin_locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)

        db.add(family)
        db.flush()

        remaining = max(0, 5 - family.pin_attempts)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid PIN ({remaining} attempts remaining)",
        )

    # PIN correct - reset attempts
    family.pin_attempts = 0
    family.pin_locked_until = None
    db.add(family)
    db.flush()

    return family
