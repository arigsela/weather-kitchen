"""
Test fixtures and configuration for pytest.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import create_app
from app.models import DeclarativeBase  # imports all models, ensuring all tables are registered
from app.models.family import Family
from app.models.recipe import Recipe
from app.models.user import User


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables for this test
    DeclarativeBase.metadata.create_all(bind=engine)

    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def test_client(test_db):
    """Create a test client with overridden database dependency."""
    import app.services.audit_service as audit_mod

    app = create_app()

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Override the session factory used by background audit tasks so they
    # write to the same in-memory test DB instead of the production engine.
    original_factory = audit_mod._session_factory
    test_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_db.get_bind())
    audit_mod._session_factory = test_session_local

    yield TestClient(app)

    audit_mod._session_factory = original_factory


@pytest.fixture
def auth_headers():
    """Helper to create authorization headers."""

    def _auth_headers(token: str = "test-token") -> dict:
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def family_factory(test_db):
    """Factory for creating test families."""

    def _create_family(
        db: Session = None,
        name: str = "test_family",
        family_size: int = 4,
        password: str = "TestPass1",
        is_active: bool = True,
    ) -> tuple[Family, str]:
        """Create a family using FamilyService. Returns (family, plaintext_token)."""
        # Use test_db if db not provided
        if db is None:
            db = test_db

        from app.services.family_service import FamilyService

        service = FamilyService(db)
        response, access_token, refresh_token = service.create_family(
            name=name,
            family_size=family_size,
            password=password,
        )

        # Retrieve the created family object
        family = db.query(Family).filter(Family.id == response.id).first()
        # Return access_token — used as Bearer token in Authorization headers
        return family, access_token

    return _create_family


@pytest.fixture
def user_factory():
    """Factory for creating test users."""

    def _create_user(
        db: Session,
        family_id,
        name: str = "Test User",
        emoji: str | None = None,
    ) -> User:
        """Create a user in a family."""
        user = User(
            id=uuid4(),
            family_id=family_id,
            name=name,
            emoji=emoji,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(user)
        db.commit()
        return user

    return _create_user


@pytest.fixture
def recipe_factory():
    """Factory for creating test recipes."""

    def _create_recipe(
        db: Session,
        name: str = "Test Recipe",
        weather: str = "sunny",
        category: str = "breakfast",
    ) -> Recipe:
        """Create a recipe."""
        recipe = Recipe(
            id=uuid4(),
            name=name,
            emoji="🍳",
            why="A delicious test recipe",
            tip="Test tip",
            serves=4,
            weather=weather,
            category=category,
            version_added="1.0.0",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(recipe)
        db.commit()
        return recipe

    return _create_recipe
