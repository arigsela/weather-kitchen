"""
PIN hashing and verification using bcrypt.
Uses bcrypt directly (not passlib, which is unmaintained).
PINs are 4-6 digit numeric codes for sensitive operations.
"""

from datetime import UTC, datetime, timedelta

import bcrypt

from app.config import settings


def hash_pin(pin: str) -> str:
    """
    Hash a PIN using bcrypt with 12 rounds.

    Args:
        pin: The PIN as a string (typically 4-6 digits)

    Returns:
        str: The bcrypt hash (encoded as string)

    Note:
        bcrypt automatically generates a salt and includes it in the hash.
        The returned value is deterministic for verification but unique per call.
    """
    # Convert PIN to bytes and hash
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    hash_digest = bcrypt.hashpw(pin.encode("utf-8"), salt)
    # Return as string (bcrypt returns bytes)
    return hash_digest.decode("utf-8")


def verify_pin(provided_pin: str, stored_hash: str) -> bool:
    """
    Verify a provided PIN against a bcrypt hash.

    Args:
        provided_pin: The PIN provided by user
        stored_hash: The bcrypt hash from database

    Returns:
        bool: True if PIN matches, False otherwise

    Example:
        >>> pin_hash = hash_pin("1234")
        >>> verify_pin("1234", pin_hash)
        True
        >>> verify_pin("5678", pin_hash)
        False
    """
    try:
        return bcrypt.checkpw(provided_pin.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # Invalid hash format
        return False


def check_lockout(pin_locked_until: datetime | None) -> tuple[bool, int]:
    """
    Check if a PIN is currently locked and return remaining lockout time.

    Args:
        pin_locked_until: Datetime when lockout expires (None if not locked)

    Returns:
        tuple[bool, int]: (is_locked, seconds_remaining)
            - is_locked: True if currently locked, False otherwise
            - seconds_remaining: Seconds until lockout expires (0 if not locked)

    Example:
        >>> # No lockout
        >>> is_locked, remaining = check_lockout(None)
        >>> is_locked, remaining
        (False, 0)

        >>> # Lockout active
        >>> future = datetime.now(timezone.utc) + timedelta(minutes=10)
        >>> is_locked, remaining = check_lockout(future)
        >>> is_locked
        True
        >>> remaining > 0
        True
    """
    if pin_locked_until is None:
        return False, 0

    now = datetime.now(UTC)
    if now < pin_locked_until:
        remaining_seconds = int((pin_locked_until - now).total_seconds())
        return True, remaining_seconds

    return False, 0


def get_lockout_until() -> datetime:
    """
    Calculate the datetime when PIN lockout should expire.

    Returns:
        datetime: Current time + PIN_LOCKOUT_MINUTES in UTC

    Example:
        >>> lockout_time = get_lockout_until()
        >>> # lockout_time is now + 15 minutes (default)
    """
    return datetime.now(UTC) + timedelta(minutes=settings.pin_lockout_minutes)


def should_lockout(pin_attempts: int) -> bool:
    """
    Determine if PIN should be locked out based on failed attempts.

    Args:
        pin_attempts: Number of failed PIN attempts

    Returns:
        bool: True if pin_attempts >= PIN_MAX_ATTEMPTS

    Example:
        >>> should_lockout(4)
        False
        >>> should_lockout(5)
        True
    """
    return pin_attempts >= settings.pin_max_attempts
