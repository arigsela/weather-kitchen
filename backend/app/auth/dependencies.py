"""
FastAPI dependency injection for JWT authentication and authorization.
"""

from datetime import datetime, timezone
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.family import Family
from app.auth.jwt import decode_token
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


async def get_current_family(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> Family:
    """
    Decode JWT access token and return the authenticated family.

    Raises 401 on missing/invalid/expired token.
    """
    token = get_token_from_header(authorization)

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    family_id = payload.get("sub")
    if not family_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    family = db.query(Family).filter(
        Family.id == family_id,
        Family.is_active == True,  # noqa: E712
    ).first()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Family not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return family


async def require_family_owner(
    family_id: UUID,
    current_family: Family = Depends(get_current_family),
) -> Family:
    """
    Verify the authenticated family ID matches the URL family_id.
    Returns 404 (not 403) to prevent family enumeration.
    """
    if current_family.id != family_id:
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
    Raises 423 if locked out, 403 if PIN incorrect.
    """
    is_locked, lockout_expires_at = check_lockout(
        family.pin_attempts,
        family.pin_locked_until,
    )
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Too many failed attempts. Try again after {lockout_expires_at}",
        )

    pin_correct = verify_pin_hash(pin, family.admin_pin_hash)

    if not pin_correct:
        family.pin_attempts += 1
        if family.pin_attempts >= 5:
            from datetime import timedelta
            family.pin_locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.add(family)
        db.flush()
        remaining = max(0, 5 - family.pin_attempts)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid PIN ({remaining} attempts remaining)",
        )

    family.pin_attempts = 0
    family.pin_locked_until = None
    db.add(family)
    db.flush()
    return family
