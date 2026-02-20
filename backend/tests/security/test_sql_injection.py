"""
Security tests for SQL injection prevention.
Tests verify that SQL injection payloads submitted through API fields are either
rejected by Pydantic validation (422) or treated as literal strings by the ORM,
and that no database errors (500) are produced in any case.
"""

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# SQL injection payload catalogue
# ---------------------------------------------------------------------------

SQL_PAYLOADS = [
    "'; DROP TABLE families; --",
    "' OR '1'='1",
    '" OR 1=1 --',
    "'; SELECT * FROM families; --",
    "' UNION SELECT id, name, api_token_hash FROM families --",
    "' UNION SELECT 1,2,3,4,5 --",
    "1; DELETE FROM users WHERE '1'='1",
    "admin'--",
    "' OR 1=1#",
    "') OR ('1'='1",
    "'; EXEC xp_cmdshell('whoami'); --",
    "' AND SLEEP(5) --",
    "1 AND 1=CONVERT(int,(SELECT TOP 1 name FROM sysobjects WHERE xtype='U'))--",
    "' AND (SELECT SUBSTRING(username,1,1) FROM users WHERE username='admin')='a'--",
    "'; WAITFOR DELAY '0:0:5'--",
]

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _assert_no_server_error(response, payload: str) -> None:
    """Assert the server did not return a 500 Internal Server Error."""
    assert response.status_code != 500, (
        f"Server returned 500 for SQL payload: {payload!r}\nResponse body: {response.text}"
    )


def _assert_payload_handled(response, payload: str) -> None:
    """Assert payload is rejected (422) or returned as literal text (200/201). Never 500."""
    _assert_no_server_error(response, payload)
    assert response.status_code in (200, 201, 409, 422), (
        f"Unexpected status {response.status_code} for payload: {payload!r}"
    )


# ---------------------------------------------------------------------------
# Family name SQL injection tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", SQL_PAYLOADS[:8])
def test_sql_injection_in_family_name_on_create(test_client: TestClient, payload: str):
    """Test that SQL injection payloads in family name on creation are handled safely."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": payload,
            "family_size": 3,
            "admin_pin": "1234",
        },
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", SQL_PAYLOADS[8:])
def test_sql_injection_in_family_name_on_update(
    test_client: TestClient, family_factory, test_db, payload: str
):
    """Test that SQL injection payloads in family name on update are handled safely."""
    family, token = family_factory(test_db)

    response = test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# User name SQL injection tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", SQL_PAYLOADS[:8])
def test_sql_injection_in_user_name(test_client: TestClient, family_factory, test_db, payload: str):
    """Test that SQL injection payloads in user name are handled safely."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", SQL_PAYLOADS[8:])
def test_sql_injection_in_user_name_additional(
    test_client: TestClient, family_factory, test_db, payload: str
):
    """Test that additional SQL injection payloads in user name are handled safely."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# Ingredient text SQL injection tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", SQL_PAYLOADS[:8])
def test_sql_injection_in_ingredient_text(
    test_client: TestClient, family_factory, user_factory, test_db, payload: str
):
    """Test that SQL injection payloads in ingredient text are handled safely."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": [payload]},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


@pytest.mark.parametrize("payload", SQL_PAYLOADS[8:])
def test_sql_injection_in_ingredient_text_additional(
    test_client: TestClient, family_factory, user_factory, test_db, payload: str
):
    """Test that additional SQL injection payloads in ingredient text are handled safely."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": [payload]},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)


# ---------------------------------------------------------------------------
# Query parameter SQL injection tests
# ---------------------------------------------------------------------------


def test_sql_injection_in_user_list_query_does_not_cause_500(
    test_client: TestClient, family_factory, test_db
):
    """Test that SQL injection in list endpoint query strings does not cause a 500 error."""
    family, token = family_factory(test_db)
    payload = "' OR '1'='1"

    response = test_client.get(
        "/api/v1/users",
        params={"search": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_no_server_error(response, payload)


def test_sql_injection_in_path_parameter_does_not_cause_500(
    test_client: TestClient, family_factory, test_db
):
    """Test that SQL injection in a path parameter does not cause a 500 error."""
    family, token = family_factory(test_db)
    payload = "' OR '1'='1"

    response = test_client.get(
        f"/api/v1/users/{payload}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (404, 422), (
        f"Unexpected status {response.status_code} for path injection payload"
    )


# ---------------------------------------------------------------------------
# Stored value integrity verification
# ---------------------------------------------------------------------------


def test_sql_payload_stored_as_literal_string_in_family_name(
    test_client: TestClient, family_factory, test_db
):
    """Verify that a SQL payload stored in family name is returned verbatim without being interpreted."""
    family, token = family_factory(test_db)
    payload = "'; SELECT name FROM families; --"

    response = test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code in (200, 201):
        data = response.json()
        assert data.get("name") == payload, (
            f"Stored name does not match literal payload. Got: {data.get('name')!r}"
        )
    else:
        assert response.status_code == 422


def test_union_select_payload_in_user_name_stored_or_rejected(
    test_client: TestClient, family_factory, test_db
):
    """Verify that a UNION SELECT payload in user name is rejected or stored as literal text."""
    family, token = family_factory(test_db)
    payload = "' UNION SELECT id, api_token_hash FROM families LIMIT 1 --"

    response = test_client.post(
        "/api/v1/users",
        json={"name": payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    _assert_payload_handled(response, payload)
    if response.status_code in (200, 201):
        data = response.json()
        assert data.get("name") == payload


def test_drop_table_payload_does_not_destroy_database(
    test_client: TestClient, family_factory, test_db
):
    """Verify that a DROP TABLE payload does not destroy database state (tables remain accessible)."""
    family, token = family_factory(test_db)
    drop_payload = "'; DROP TABLE families; --"

    test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": drop_payload},
        headers={"Authorization": f"Bearer {token}"},
    )

    check_response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert check_response.status_code == 200, (
        "Family table appears to have been destroyed by DROP TABLE injection"
    )
