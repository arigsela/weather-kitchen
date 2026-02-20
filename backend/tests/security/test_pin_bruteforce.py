"""
Security tests for PIN brute-force protection and lockout behavior.
Tests verify that the PIN lockout mechanism engages after 5 failed attempts
and that lockout is family-scoped (does not bleed across families).
"""

from fastapi.testclient import TestClient


def test_correct_pin_returns_success_true(test_client: TestClient, family_factory, test_db):
    """Test that the correct PIN on verify-pin returns success=true."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_wrong_pin_returns_success_false(test_client: TestClient, family_factory, test_db):
    """Test that an incorrect PIN on verify-pin returns success=false with a 200 status."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "9999"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


def test_four_failures_then_correct_pin_succeeds(test_client: TestClient, family_factory, test_db):
    """Test that 4 wrong PIN attempts followed by the correct PIN resets counter and returns success=true."""
    family, token = family_factory(test_db, admin_pin="1234")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(4):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-pin",
            json={"admin_pin": "0000"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_five_failures_triggers_lockout(test_client: TestClient, family_factory, test_db):
    """Test that 5 consecutive wrong PIN attempts result in brute-force protection (lockout or rate limit)."""
    family, token = family_factory(test_db, admin_pin="1234")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(5):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-pin",
            json={"admin_pin": "0000"},
            headers=headers,
        )
        # Each attempt either gets through (200) or is rate-limited (429)
        assert resp.status_code in (200, 429)

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234"},
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
    family, token = family_factory(test_db, admin_pin="1234")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(5):
        resp = test_client.post(
            f"/api/v1/families/{family.id}/verify-pin",
            json={"admin_pin": "0000"},
            headers=headers,
        )
        assert resp.status_code in (200, 429)

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234"},
        headers=headers,
    )
    # Brute-force protection active: either rate-limited or application lockout
    assert response.status_code in (200, 429)
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is False
        assert data.get("message") is not None
        assert len(data["message"]) > 0


def test_pin_lockout_does_not_affect_other_family(test_client: TestClient, family_factory, test_db):
    """Test that PIN brute-force protection for one family does not prevent another family from verifying."""
    family1, token1 = family_factory(test_db, name="Locked Family", admin_pin="1111")
    family2, token2 = family_factory(test_db, name="Healthy Family", admin_pin="2222")

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    for _ in range(5):
        test_client.post(
            f"/api/v1/families/{family1.id}/verify-pin",
            json={"admin_pin": "0000"},
            headers=headers1,
        )

    # Other family's request may still be rate-limited by IP (same testclient IP),
    # but the PIN lockout itself is family-scoped
    response = test_client.post(
        f"/api/v1/families/{family2.id}/verify-pin",
        json={"admin_pin": "2222"},
        headers=headers2,
    )
    # Accept either success or rate-limit (rate limiter is IP-based, not family-based)
    assert response.status_code in (200, 429)
    if response.status_code == 200:
        assert response.json()["success"] is True


def test_non_numeric_pin_rejected_with_422(test_client: TestClient, family_factory, test_db):
    """Test that a PIN containing non-numeric characters is rejected with 422 validation error."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "abcd"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_pin_longer_than_six_digits_rejected_with_422(
    test_client: TestClient, family_factory, test_db
):
    """Test that a PIN longer than 6 digits is rejected with 422 validation error."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234567"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_pin_shorter_than_four_digits_rejected_with_422(
    test_client: TestClient, family_factory, test_db
):
    """Test that a PIN shorter than 4 digits is rejected with 422 validation error."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_empty_pin_rejected_with_422(test_client: TestClient, family_factory, test_db):
    """Test that an empty string PIN is rejected with 422 validation error."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
