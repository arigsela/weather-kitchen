"""
Test fixtures and configuration for pytest.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.base import DeclarativeBase
from app.database import get_db


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
