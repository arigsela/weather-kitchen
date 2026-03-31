"""
Security tests for input validation on API endpoints.
Tests verify that Pydantic schemas enforce field constraints correctly and
that boundary conditions, out-of-range values, and dangerous inputs are
consistently rejected with 422 Unprocessable Entity responses.
"""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Family creation validation tests
# ---------------------------------------------------------------------------


def test_empty_family_name_rejected_with_422(test_client: TestClient):
    """Test that an empty family name is rejected during family creation."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "",
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_name_exceeding_max_length_rejected_with_422(test_client: TestClient):
    """Test that a family name longer than 100 characters is rejected."""
    long_name = "A" * 101
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": long_name,
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_name_at_max_length_accepted(test_client: TestClient):
    """Test that a family name of exactly 100 characters is accepted."""
    max_name = "B" * 100
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": max_name,
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 201


def test_family_size_zero_rejected_with_422(test_client: TestClient):
    """Test that a family size of 0 is rejected (minimum is 1)."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 0,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_size_negative_rejected_with_422(test_client: TestClient):
    """Test that a negative family size is rejected."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": -1,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_size_999_rejected_with_422(test_client: TestClient):
    """Test that a family size of 999 is rejected (maximum is 20)."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 999,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_size_21_rejected_with_422(test_client: TestClient):
    """Test that a family size of 21 is rejected (maximum is 20)."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 21,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_family_size_at_maximum_accepted(test_client: TestClient):
    """Test that a family size of exactly 20 is accepted."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Large Family",
            "family_size": 20,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# Password validation tests
# ---------------------------------------------------------------------------


def test_password_too_short_rejected_with_422(test_client: TestClient):
    """Test that a password shorter than 8 characters is rejected."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "Short1",
        },
    )
    assert response.status_code == 422


def test_password_no_uppercase_rejected_with_422(test_client: TestClient):
    """Test that a password without uppercase letters is rejected."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "alllowercase1",
        },
    )
    assert response.status_code == 422


def test_password_no_lowercase_rejected_with_422(test_client: TestClient):
    """Test that a password without lowercase letters is rejected."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "ALLUPPERCASE1",
        },
    )
    assert response.status_code == 422


def test_password_no_digit_rejected_with_422(test_client: TestClient):
    """Test that a password without any digit is rejected."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "NoDigitsHere",
        },
    )
    assert response.status_code == 422


def test_valid_password_accepted(test_client: TestClient):
    """Test that a valid password (min 8 chars, 1 upper, 1 lower, 1 digit) is accepted."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 201


def test_password_with_special_characters_accepted(test_client: TestClient):
    """Test that a valid password containing special characters is accepted."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "password": "Test!@Pass1",
        },
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# User creation validation tests
# ---------------------------------------------------------------------------


def test_empty_user_name_rejected_with_422(test_client: TestClient, family_factory, test_db):
    """Test that an empty user name is rejected during user creation."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_user_name_exceeding_max_length_rejected_with_422(
    test_client: TestClient, family_factory, test_db
):
    """Test that a user name exceeding 100 characters is rejected."""
    family, token = family_factory(test_db)
    long_name = "U" * 101

    response = test_client.post(
        "/api/v1/users",
        json={"name": long_name},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_user_name_at_max_length_accepted(test_client: TestClient, family_factory, test_db):
    """Test that a user name of exactly 100 characters is accepted."""
    family, token = family_factory(test_db)
    max_name = "V" * 100

    response = test_client.post(
        "/api/v1/users",
        json={"name": max_name},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# Null byte and edge-case string tests
# ---------------------------------------------------------------------------


def test_null_byte_in_family_name_rejected_or_sanitized(test_client: TestClient):
    """Test that null bytes in family name are rejected (422) or sanitized by the system."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Family\x00Name",
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code in (201, 422)
    if response.status_code == 201:
        stored_name = response.json().get("name", "")
        assert "\x00" not in stored_name


def test_null_byte_in_user_name_rejected_or_sanitized(
    test_client: TestClient, family_factory, test_db
):
    """Test that null bytes in user name are rejected (422) or sanitized by the system."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": "User\x00Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (201, 422)
    if response.status_code == 201:
        stored_name = response.json().get("name", "")
        assert "\x00" not in stored_name


def test_whitespace_only_family_name_rejected_or_treated_as_valid(test_client: TestClient):
    """Test that a whitespace-only family name is either rejected (422) or accepted with length > 0."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "   ",
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code in (201, 422)


def test_missing_required_field_family_name_rejected_with_422(test_client: TestClient):
    """Test that omitting the required family name field results in a 422 error."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "family_size": 4,
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422


def test_missing_required_field_password_rejected_with_422(test_client: TestClient):
    """Test that omitting the required password field results in a 422 error."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
        },
    )
    assert response.status_code == 422


def test_missing_required_field_family_size_rejected_with_422(test_client: TestClient):
    """Test that omitting the required family_size field results in a 422 error."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "password": "TestPass1",
        },
    )
    assert response.status_code == 422
