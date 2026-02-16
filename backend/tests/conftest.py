"""
Test fixtures and configuration for pytest.
"""

from datetime import datetime, timezone
from uuid import uuid4
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.base import DeclarativeBase
from app.models.family import Family
from app.models.user import User
from app.models.recipe import Recipe
from app.database import get_db
from app.auth.token import generate_api_token, hash_token
from app.auth.pin import hash_pin


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
    app = create_app()

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


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
        name: str = "Test Family",
        family_size: int = 4,
        admin_pin: str = "1234",
        is_active: bool = True,
    ) -> tuple[Family, str]:
        """Create a family using FamilyService. Returns (family, plaintext_token)."""
        # Use test_db if db not provided
        if db is None:
            db = test_db

        from app.services.family_service import FamilyService
        service = FamilyService(db)
        response, token = service.create_family(
            name=name,
            family_size=family_size,
            admin_pin=admin_pin,
        )

        # Retrieve the created family object
        family = db.query(Family).filter(Family.id == response.id).first()
        return family, token

    return _create_family


@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def _create_user(
        db: Session,
        family_id,
        name: str = "Test User",
        age: int = 10,
    ) -> User:
        """Create a user in a family."""
        user = User(
            id=uuid4(),
            family_id=family_id,
            name=name,
            age=age,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
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
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(recipe)
        db.commit()
        return recipe

    return _create_recipe
