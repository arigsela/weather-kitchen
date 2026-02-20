"""
Security tests for rate limiting middleware.
Tests verify that the in-memory rate limiter engages under rapid traffic
and returns 429 Too Many Requests with a Retry-After header.

Note: Each test function receives a fresh test_client (function-scoped fixture),
which resets the in-memory rate limiter state for that test app instance.
Rapid sequential requests within a single test are used to exhaust the limits.
"""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# General rate limiting (10 req/sec per IP)
# ---------------------------------------------------------------------------


def test_rapid_requests_to_health_trigger_429(test_client: TestClient):
    """Test that sending 15 rapid requests to /health causes at least one 429 response."""
    status_codes = []
    for _ in range(15):
        response = test_client.get("/health")
        status_codes.append(response.status_code)

    assert 429 in status_codes, (
        f"Expected at least one 429 among {len(status_codes)} rapid requests, "
        f"got status codes: {status_codes}"
    )


def test_429_response_includes_retry_after_header(test_client: TestClient):
    """Test that a 429 response includes a Retry-After header."""
    retry_after_found = False
    for _ in range(20):
        response = test_client.get("/health")
        if response.status_code == 429:
            assert "retry-after" in response.headers or "Retry-After" in response.headers, (
                f"429 response missing Retry-After header. Headers: {dict(response.headers)}"
            )
            retry_after_found = True
            break

    assert retry_after_found, (
        "Rate limiter never returned 429 within 20 rapid requests. "
        "Verify the rate limit threshold is low enough to trigger in tests."
    )


def test_429_response_body_has_error_message(test_client: TestClient):
    """Test that a 429 response body contains a meaningful error message."""
    for _ in range(20):
        response = test_client.get("/health")
        if response.status_code == 429:
            body = response.json()
            assert "detail" in body or "message" in body or "error" in body, (
                f"429 response body missing error message. Body: {body}"
            )
            message_text = body.get("detail") or body.get("message") or body.get("error") or ""
            assert len(str(message_text)) > 0, f"429 response error message is empty. Body: {body}"
            return

    assert False, "Rate limiter never returned 429 within 20 rapid requests."


def test_rate_limit_recovers_after_window(test_client: TestClient, family_factory, test_db):
    """Test that requests succeed on a fresh client (simulating a new rate limit window)."""
    family, token = family_factory(test_db)
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# PIN endpoint rate limiting (5 req / 15 min per IP)
# ---------------------------------------------------------------------------


def test_rapid_pin_verify_requests_trigger_429(test_client: TestClient, family_factory, test_db):
    """Test that sending 10 rapid POST requests to verify-pin causes at least one 429 response."""
    family, token = family_factory(test_db, admin_pin="1234")
    headers = {"Authorization": f"Bearer {token}"}

    status_codes = []
    for _ in range(10):
        response = test_client.post(
            f"/api/v1/families/{family.id}/verify-pin",
            json={"admin_pin": "1234"},
            headers=headers,
        )
        status_codes.append(response.status_code)

    assert 429 in status_codes, (
        f"Expected at least one 429 among 10 rapid PIN verify requests, "
        f"got status codes: {status_codes}"
    )


def test_rapid_token_rotate_requests_trigger_429(test_client: TestClient, family_factory, test_db):
    """Test that sending rapid POST requests to token/rotate causes at least one 429 response."""
    family, token = family_factory(test_db, admin_pin="1234")
    status_codes = []

    for _ in range(10):
        response = test_client.post(
            f"/api/v1/families/{family.id}/token/rotate",
            json={"admin_pin": "1234"},
            headers={"Authorization": f"Bearer {token}"},
        )
        status_codes.append(response.status_code)
        if response.status_code == 200:
            token = response.json().get("api_token", token)

    assert 429 in status_codes, (
        f"Expected at least one 429 among rapid token rotate requests, "
        f"got status codes: {status_codes}"
    )


def test_pin_endpoint_429_includes_retry_after_header(
    test_client: TestClient, family_factory, test_db
):
    """Test that a 429 from a PIN endpoint includes a Retry-After header."""
    family, token = family_factory(test_db, admin_pin="1234")
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(10):
        response = test_client.post(
            f"/api/v1/families/{family.id}/verify-pin",
            json={"admin_pin": "1234"},
            headers=headers,
        )
        if response.status_code == 429:
            assert "retry-after" in response.headers or "Retry-After" in response.headers, (
                f"PIN 429 response missing Retry-After header. Headers: {dict(response.headers)}"
            )
            return

    assert False, "PIN rate limiter never returned 429 within 10 rapid requests."
