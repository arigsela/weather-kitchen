"""
JWT token creation and verification utilities.
Access tokens: 15-minute TTL, contain family_id claim.
Refresh tokens: 7-day TTL, contain family_id + jti (unique ID for revocation).
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(family_id: str) -> str:
    """
    Create a signed JWT access token for a family.

    Args:
        family_id: UUID string of the family

    Returns:
        Signed JWT string (compact serialization)
    """
    expire = _now() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(family_id),
        "type": "access",
        "iat": _now(),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(family_id: str) -> tuple[str, str]:
    """
    Create a signed JWT refresh token and its SHA256 hash for DB storage.

    Args:
        family_id: UUID string of the family

    Returns:
        tuple[str, str]: (plaintext_token, sha256_hash)
    """
    jti = str(uuid.uuid4())
    expire = _now() + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(family_id),
        "type": "refresh",
        "jti": jti,
        "iat": _now(),
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    token_hash = hash_refresh_token(token)
    return token, token_hash


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT string

    Returns:
        Claims dict

    Raises:
        jwt.ExpiredSignatureError: if token is expired
        jwt.InvalidTokenError: if token is malformed or signature invalid
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def hash_refresh_token(token: str) -> str:
    """SHA256 hash of a refresh token for DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()
