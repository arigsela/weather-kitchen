"""
Base model classes with UUID primary keys and timestamps.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base, declared_attr

from app.database import GUID


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps to models."""

    @declared_attr
    def created_at(cls):  # noqa: N805
        return Column(DateTime, default=datetime.now(UTC), nullable=False)

    @declared_attr
    def updated_at(cls):  # noqa: N805
        return Column(
            DateTime,
            default=datetime.now(UTC),
            onupdate=datetime.now(UTC),
            nullable=False,
        )


class UUIDMixin:
    """Mixin that adds a UUID primary key to models."""

    @declared_attr
    def id(cls):  # noqa: N805
        return Column(
            GUID,
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )


class Base(TimestampMixin, UUIDMixin):
    """
    Base class for all SQLAlchemy ORM models.
    Includes UUID primary key and timestamps (created_at, updated_at).
    """

    __abstract__ = True


# SQLAlchemy declarative base
DeclarativeBase = declarative_base(cls=Base)
