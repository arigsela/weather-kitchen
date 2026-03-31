"""
Password hashing, verification, and strength validation using bcrypt.
Replaces PIN-based auth for family login and sensitive operations.
"""

import re

import bcrypt

from app.config import settings


class PasswordValidationError(ValueError):
    """Raised when a password fails strength validation."""


def validate_password_strength(password: str) -> str:
    """
    Validate password meets minimum strength requirements.

    Rules:
        - Minimum 8 characters (configurable)
        - Maximum 128 characters
        - At least 1 uppercase letter (A-Z)
        - At least 1 lowercase letter (a-z)
        - At least 1 digit (0-9)
        - No null bytes

    Args:
        password: The plaintext password to validate

    Returns:
        The password if valid

    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    if "\x00" in password:
        raise PasswordValidationError("Password must not contain null bytes")

    if len(password) < settings.password_min_length:
        raise PasswordValidationError(
            f"Password must be at least {settings.password_min_length} characters"
        )

    if len(password) > settings.password_max_length:
        raise PasswordValidationError(
            f"Password must be at most {settings.password_max_length} characters"
        )

    if not re.search(r"[A-Z]", password):
        raise PasswordValidationError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise PasswordValidationError("Password must contain at least one lowercase letter")

    if not re.search(r"[0-9]", password):
        raise PasswordValidationError("Password must contain at least one digit")

    return password


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plaintext password

    Returns:
        The bcrypt hash as a string
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(provided_password: str, stored_hash: str) -> bool:
    """
    Verify a provided password against a bcrypt hash.

    Args:
        provided_password: The password provided by user
        stored_hash: The bcrypt hash from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(provided_password.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
