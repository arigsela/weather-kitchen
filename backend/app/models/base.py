"""
Base model classes with UUID primary keys and timestamps.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr

from app.database import GUID


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps to models."""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.now(timezone.utc),
            onupdate=datetime.now(timezone.utc),
            nullable=False,
        )


class UUIDMixin:
    """Mixin that adds a UUID primary key to models."""

    @declared_attr
    def id(cls):
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
