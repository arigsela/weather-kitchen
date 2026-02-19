"""
API Token generation and hashing.
Tokens are high-entropy random values (256 bits) encoded as URL-safe base64.
Hashes are SHA256 digests stored in the database for comparison.
"""

import hashlib
import secrets

from app.config import settings


def generate_api_token() -> tuple[str, str]:
    """
    Generate a new API token and its hash.

    Returns:
        tuple[str, str]: (plaintext_token, sha256_hash)
            - plaintext_token: One-time shown to user (43-44 characters)
            - sha256_hash: Stored in database for verification (64 hex characters)

    Example:
        >>> token, token_hash = generate_api_token()
        >>> # token: "KdLqM8nP_vW3xYzA1bCdEfGhIjKlMnOpQrStUvWxYz"
        >>> # token_hash: "abc123def456..."
    """
    # Generate high-entropy random bytes and encode as URL-safe base64
    token = secrets.token_urlsafe(settings.token_byte_length)

    # Hash the token for storage
    token_hash = hash_token(token)

    return token, token_hash


def hash_token(token: str) -> str:
    """
    Hash an API token using SHA256.

    Args:
        token: The plaintext API token

    Returns:
        str: SHA256 hash in hexadecimal format (64 characters)

    Note:
        This is a one-way function. Tokens are hashed before storage.
        During authentication, we hash the provided token and compare
        it to the stored hash using constant-time comparison.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(provided_token: str, stored_hash: str) -> bool:
    """
    Verify a provided token against a stored hash.
    Uses constant-time comparison to prevent timing attacks.

    Args:
        provided_token: Token provided by client in Authorization header
        stored_hash: SHA256 hash stored in database

    Returns:
        bool: True if token is valid, False otherwise

    Example:
        >>> token, token_hash = generate_api_token()
        >>> verify_token(token, token_hash)
        True
        >>> verify_token("wrong_token", token_hash)
        False
    """
    provided_hash = hash_token(provided_token)
    return secrets.compare_digest(provided_hash, stored_hash)
