"""
Unit tests for FamilyService - token generation, password lockout, consent flow.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.services.family_service import FamilyService


def test_create_family_generates_token(test_db: Session):
    """Test that family creation generates a JWT access + refresh token pair."""
    service = FamilyService(test_db)
    response, access_token, refresh_token = service.create_family(
        name="test_family",
        family_size=4,
        password="TestPass1",
    )

    assert response.id is not None
    assert response.name == "test_family"
    assert response.family_size == 4
    assert response.is_active is True
    # JWT tokens have 2 dots (3 parts: header.payload.signature)
    assert access_token.count(".") == 2
    assert refresh_token.count(".") == 2


def test_create_family_hashes_password(test_db: Session):
    """Test that password is properly hashed."""
    service = FamilyService(test_db)
    password = "TestPass2"
    response, access_token, refresh_token = service.create_family(
        name="Password Test Family",
        family_size=2,
        password=password,
    )

    # Verify password can be verified
    verified, message = service.verify_pin(response.id, password)
    assert verified is True
    assert message is None


def test_verify_pin_wrong_password_fails(test_db: Session, family_factory):
    """Test that wrong password fails verification."""
    family, token = family_factory(test_db, password="TestPass1")
    service = FamilyService(test_db)

    verified, message = service.verify_pin(family.id, "WrongPass1")
    assert verified is False
    assert "Invalid PIN" in message


def test_pin_lockout_after_5_attempts(test_db: Session, family_factory):
    """Test that password locks after 5 failed attempts."""
    family, token = family_factory(test_db, password="TestPass1")
    service = FamilyService(test_db)

    # Make 5 failed attempts
    for i in range(5):
        verified, message = service.verify_pin(family.id, "WrongPass1")
        assert verified is False

    # 6th attempt should trigger lockout
    verified, message = service.verify_pin(family.id, "TestPass1")
    assert verified is False
    assert "Locked until" in message


def test_pin_lockout_expires_after_15_minutes(test_db: Session, family_factory):
    """Test that password lockout expires after 15 minutes."""
    family, token = family_factory(test_db, password="TestPass1")
    service = FamilyService(test_db)

    # Trigger lockout
    for i in range(5):
        service.verify_pin(family.id, "WrongPass1")

    # Set lockout to past
    family.pin_locked_until = datetime.now(UTC) - timedelta(seconds=1)
    test_db.commit()

    # Should now work
    verified, message = service.verify_pin(family.id, "TestPass1")
    assert verified is True


def test_successful_pin_resets_attempts(test_db: Session, family_factory):
    """Test that successful password verification resets attempt counter."""
    family, token = family_factory(test_db, password="TestPass1")
    service = FamilyService(test_db)

    # Make 2 failed attempts
    for i in range(2):
        service.verify_pin(family.id, "WrongPass1")

    # Verify correct password
    verified, message = service.verify_pin(family.id, "TestPass1")
    assert verified is True

    # Should be able to make more failed attempts without lockout
    for i in range(3):
        service.verify_pin(family.id, "WrongPass1")
    verified, _ = service.verify_pin(family.id, "TestPass1")
    assert verified is True


def test_rotate_token_generates_new_token(test_db: Session, family_factory):
    """Test that token rotation issues a new JWT access + refresh pair."""
    family, old_access_token = family_factory(test_db, password="TestPass1")
    service = FamilyService(test_db)

    new_access, new_refresh = service.rotate_tokens(family.id)
    assert new_access is not None
    assert new_refresh is not None
    # Both are valid JWTs (3 parts: header.payload.signature)
    assert new_access.count(".") == 2
    assert new_refresh.count(".") == 2
    # Refresh token has a unique jti — always different from original
    assert new_refresh != old_access_token


def test_soft_delete_marks_inactive(test_db: Session, family_factory):
    """Test that soft delete marks family as inactive."""
    family, token = family_factory(test_db)
    service = FamilyService(test_db)

    success = service.soft_delete(family.id)
    assert success is True

    # Verify family is inactive
    test_db.refresh(family)
    assert family.is_active is False


def test_hard_delete_removes_family(test_db: Session, family_factory):
    """Test that hard delete permanently removes family."""
    family, token = family_factory(test_db)
    family_id = family.id
    service = FamilyService(test_db)

    success = service.hard_delete(family_id)
    assert success is True

    # Verify family is gone
    retrieved = service.get_family(family_id)
    assert retrieved is None


def test_export_family_data_includes_all_data(test_db: Session, family_factory, user_factory):
    """Test that family data export includes all relevant data."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)  # noqa: F841

    service = FamilyService(test_db)
    exported = service.export_family_data(family.id)

    assert exported is not None
    assert "family" in exported
    assert "users" in exported
    assert "audit_log" in exported
    assert "export_date" in exported
    assert exported["family"]["name"] == family.name
