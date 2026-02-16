"""
Base repository with common CRUD operations.
"""

from typing import TypeVar, Generic, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository with common CRUD operations."""

    def __init__(self, db: Session, model_class: type[T]):
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        return self.db.query(self.model_class).filter(
            self.model_class.id == id
        ).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all entities with pagination."""
        return self.db.query(self.model_class).limit(limit).offset(offset).all()

    def count(self) -> int:
        """Get total count of entities."""
        return self.db.query(func.count(self.model_class.id)).scalar() or 0

    def create(self, **kwargs) -> T:
        """Create new entity."""
        entity = self.model_class(**kwargs)
        self.db.add(entity)
        self.db.flush()
        return entity

    def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Update entity by ID."""
        entity = self.get_by_id(id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.db.flush()
        return entity

    def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        entity = self.get_by_id(id)
        if not entity:
            return False

        self.db.delete(entity)
        self.db.flush()
        return True

    def commit(self) -> None:
        """Commit pending changes."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback pending changes."""
        self.db.rollback()
