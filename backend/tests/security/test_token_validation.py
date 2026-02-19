"""
Security tests for API token validation.
Tests verify that only valid, well-formed tokens are accepted and that
malformed, manipulated, or expired tokens are consistently rejected with 401.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


def test_valid_token_returns_200(test_client: TestClient, family_factory, test_db):
    """Test that a valid bearer token grants access to the family endpoint."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_token_with_leading_whitespace_accepted(test_client: TestClient, family_factory, test_db):
    """Test that extra whitespace between Bearer and token is handled by split()."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer  {token}"},
    )
    # split() strips whitespace — valid token is extracted correctly
    assert response.status_code == 200


def test_token_with_trailing_whitespace_accepted(test_client: TestClient, family_factory, test_db):
    """Test that trailing whitespace after token is handled by split()."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token} "},
    )
    # split() strips whitespace — valid token is extracted correctly
    assert response.status_code == 200


def test_token_with_null_bytes_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that a token containing null bytes is rejected."""
    family, token = family_factory(test_db)
    null_byte_token = token[:10] + "\x00" + token[10:]

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {null_byte_token}"},
    )
    assert response.status_code == 401


def test_very_long_token_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that an excessively long token (10000 characters) is rejected."""
    family, token = family_factory(test_db)
    oversized_token = "a" * 10000

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {oversized_token}"},
    )
    assert response.status_code == 401


def test_token_with_unicode_characters_rejected(test_client: TestClient, family_factory, test_db):
    """Test that a token containing unicode characters is rejected at the HTTP transport layer."""
    family, token = family_factory(test_db)
    unicode_token = "токен-безопасности-юникод"

    # HTTP headers are ASCII-only (RFC 7230) — httpx correctly rejects non-ASCII values
    with pytest.raises(UnicodeEncodeError):
        test_client.get(
            f"/api/v1/families/{family.id}",
            headers={"Authorization": f"Bearer {unicode_token}"},
        )


def test_token_with_semicolons_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that a token containing semicolons (SQL-like separators) is rejected."""
    family, token = family_factory(test_db)
    malicious_token = "validtoken; DROP TABLE families; --"

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {malicious_token}"},
    )
    assert response.status_code == 401


def test_token_with_single_quotes_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that a token containing single quotes is rejected."""
    family, token = family_factory(test_db)
    malicious_token = "' OR '1'='1"

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {malicious_token}"},
    )
    assert response.status_code == 401


def test_rotation_new_refresh_token_cannot_reuse_old(
    test_client: TestClient, family_factory, test_db
):
    """After JWT rotation, the old refresh token is revoked and cannot generate a new access token."""
    family, old_token = family_factory(test_db, admin_pin="1234")

    # Get the initial refresh token by creating the family via API
    create_response = test_client.post(
        "/api/v1/families",
        json={"name": "Rotate Test", "family_size": 2, "admin_pin": "5678"},
    )
    assert create_response.status_code == 201
    old_refresh = create_response.json()["refresh_token"]
    access = create_response.json()["access_token"]
    fid = create_response.json()["id"]

    # Rotate — revokes old refresh token
    rotate_response = test_client.post(
        f"/api/v1/families/{fid}/token/rotate",
        json={"admin_pin": "5678"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert rotate_response.status_code == 200

    # Old refresh token should now be rejected
    refresh_response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert refresh_response.status_code == 401


def test_empty_string_token_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that an empty string as a token value is rejected."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": "Bearer "},
    )
    assert response.status_code == 401


def test_valid_uuid_not_a_real_token_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that a syntactically valid UUID used as a token is rejected when it has no matching record."""
    family, token = family_factory(test_db)
    fake_uuid_token = str(uuid.uuid4())

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {fake_uuid_token}"},
    )
    assert response.status_code == 401


def test_sql_injection_in_token_field_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that SQL injection payloads in the token header are rejected."""
    family, token = family_factory(test_db)
    sql_injection_token = "' UNION SELECT api_token_hash FROM families --"

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {sql_injection_token}"},
    )
    assert response.status_code == 401


def test_token_with_newline_injection_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that a token with embedded newline characters (header injection) is rejected."""
    family, token = family_factory(test_db)
    header_injection_token = "sometoken\r\nX-Injected-Header: malicious"

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {header_injection_token}"},
    )
    assert response.status_code in (400, 401)


def test_rotated_token_new_token_still_works(test_client: TestClient, family_factory, test_db):
    """After rotation the new access token grants access."""
    family, old_token = family_factory(test_db, admin_pin="5678")

    rotate_response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"admin_pin": "5678"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert rotate_response.status_code == 200
    new_token = rotate_response.json()["access_token"]

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert response.status_code == 200


def test_bearer_prefix_case_insensitive_accepted(test_client: TestClient, family_factory, test_db):
    """Test that lowercase 'bearer' prefix is accepted per RFC 7235 (case-insensitive scheme)."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"bearer {token}"},
    )
    assert response.status_code == 200
