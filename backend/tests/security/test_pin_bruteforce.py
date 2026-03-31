"""
Security tests for password brute-force protection and lockout behavior.
Tests verify that the password lockout mechanism engages after 5 failed attempts
and that lockout is family-scoped (does not bleed across families).
"""

from fastapi.testclient import TestClient


def test_correct_password_returns_success_true(test_client: TestClient, family_factory, test_db):
    """Test that the correct password on verify-password returns success=true."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_wrong_password_returns_success_false(test_client: TestClient, family_factory, test_db):
    """Test that an incorrect password on verify-password returns success=false with a 200 status."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "WrongPass1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


def test_four_failures_then_correct_password_succeeds(
    test_client: TestClient, family_factory, test_db
):
    """Test that 4 wrong password attempts followed by the correct password resets counter and returns success=true."""
    family, token = family_factory(test_db, password="TestPass1")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(4):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-password",
            json={"password": "WrongPass1"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_five_failures_triggers_lockout(test_client: TestClient, family_factory, test_db):
    """Test that 5 consecutive wrong password attempts result in brute-force protection (lockout or rate limit)."""
    family, token = family_factory(test_db, password="TestPass1")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(5):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-password",
            json={"password": "WrongPass1"},
            headers=headers,
        )
        # Each attempt either gets through (200) or is rate-limited (429)
        assert resp.status_code in (200, 429)

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
        headers=headers,
    )
    # Either rate-limited (429) or application-level lockout (200 with success=false)
    assert response.status_code in (200, 429)
    if response.status_code == 200:
        assert response.json()["success"] is False


def test_locked_family_returns_lockout_or_rate_limit(
    test_client: TestClient, family_factory, test_db
):
    """Test that after 5 failures, subsequent attempts are blocked by lockout or rate limiter."""
    family, token = family_factory(test_db, password="TestPass1")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(5):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-password",
            json={"password": "WrongPass1"},
            headers=headers,
        )
        assert resp.status_code in (200, 429)

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
        headers=headers,
    )
    # Brute-force protection active: either rate-limited or application lockout
    assert response.status_code in (200, 429)
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is False
        assert data.get("message") is not None
        assert len(data["message"]) > 0


def test_password_lockout_does_not_affect_other_family(
    test_client: TestClient, family_factory, test_db
):
    """Test that password brute-force protection for one family does not prevent another family from verifying."""
    family1, token1 = family_factory(test_db, name="locked_family", password="TestPass1")
    family2, token2 = family_factory(test_db, name="healthy_family", password="TestPass2")

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    for _ in range(5):
        test_client.post(
            f"/api/v1/families/{family1.id}/verify-password",
            json={"password": "WrongPass1"},
            headers=headers1,
        )

    # Other family's request may still be rate-limited by IP (same testclient IP),
    # but the password lockout itself is family-scoped
    response = test_client.post(
        f"/api/v1/families/{family2.id}/verify-password",
        json={"password": "TestPass2"},
        headers=headers2,
    )
    # Accept either success or rate-limit (rate limiter is IP-based, not family-based)
    assert response.status_code in (200, 429)
    if response.status_code == 200:
        assert response.json()["success"] is True


def test_password_too_short_rejected_on_create(test_client: TestClient):
    """Test that a password shorter than 8 characters is rejected during family creation."""
    response = test_client.post(
        "/api/v1/families",
        json={"name": "Test", "family_size": 4, "password": "Short1"},
    )
    assert response.status_code == 422


def test_password_no_uppercase_rejected_on_create(test_client: TestClient):
    """Test that a password without uppercase letters is rejected during family creation."""
    response = test_client.post(
        "/api/v1/families",
        json={"name": "Test", "family_size": 4, "password": "alllowercase1"},
    )
    assert response.status_code == 422


def test_password_no_lowercase_rejected_on_create(test_client: TestClient):
    """Test that a password without lowercase letters is rejected during family creation."""
    response = test_client.post(
        "/api/v1/families",
        json={"name": "Test", "family_size": 4, "password": "ALLUPPERCASE1"},
    )
    assert response.status_code == 422


def test_empty_password_rejected_with_422(test_client: TestClient, family_factory, test_db):
    """Test that an empty string password is rejected with 422 validation error."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
