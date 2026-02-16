"""
Unit tests for UserService - CRUD, ingredient management, favorites.
"""

from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.models.user import UserIngredient, UserFavorite


def test_create_user_in_family(test_db: Session, family_factory):
    """Test creating a user in a family."""
    family, token = family_factory(test_db)
    service = UserService(test_db)

    response = service.create_user(
        family_id=family.id,
        name="Child User",
        age=10,
    )

    assert response.id is not None
    assert response.family_id == family.id
    assert response.name == "Child User"
    assert response.age == 10


def test_get_user_by_id(test_db: Session, family_factory, user_factory):
    """Test retrieving user by ID with family ownership."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id, name="Get User Test")
    service = UserService(test_db)

    response = service.get_user(user.id, family.id)
    assert response is not None
    assert response.id == user.id
    assert response.name == "Get User Test"


def test_get_user_wrong_family_returns_none(test_db: Session, family_factory, user_factory):
    """Test that getting user from wrong family returns None."""
    family1, _ = family_factory(test_db, name="Family 1")
    family2, _ = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)
    service = UserService(test_db)

    response = service.get_user(user.id, family2.id)
    assert response is None


def test_list_users_in_family(test_db: Session, family_factory, user_factory):
    """Test listing users in a family."""
    family, token = family_factory(test_db)
    user1 = user_factory(test_db, family_id=family.id, name="Alice")
    user2 = user_factory(test_db, family_id=family.id, name="Bob")
    service = UserService(test_db)

    response = service.list_users(family.id)
    assert response.family_id == family.id
    assert response.total == 2
    assert len(response.users) == 2


def test_update_user_name(test_db: Session, family_factory, user_factory):
    """Test updating user name."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id, name="Original Name")
    service = UserService(test_db)

    response = service.update_user(
        user_id=user.id,
        family_id=family.id,
        name="Updated Name",
    )

    assert response is not None
    assert response.name == "Updated Name"


def test_update_user_age(test_db: Session, family_factory, user_factory):
    """Test updating user age."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id, age=10)
    service = UserService(test_db)

    response = service.update_user(
        user_id=user.id,
        family_id=family.id,
        age=12,
    )

    assert response is not None
    assert response.age == 12


def test_get_empty_ingredients(test_db: Session, family_factory, user_factory):
    """Test getting ingredients for user with no ingredients."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    service = UserService(test_db)

    response = service.get_ingredients(user.id, family.id)
    assert response is not None
    assert response.user_id == user.id
    assert response.ingredients == []


def test_update_ingredients_replaces_all(test_db: Session, family_factory, user_factory):
    """Test that update_ingredients replaces all ingredients (PUT semantics)."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    service = UserService(test_db)

    # Add initial ingredients
    ingredients_v1 = ["apple", "banana", "carrot"]
    response = service.update_ingredients(user.id, family.id, ingredients_v1)
    assert len(response.ingredients) == 3

    # Replace with new ingredients
    ingredients_v2 = ["milk", "cheese"]
    response = service.update_ingredients(user.id, family.id, ingredients_v2)
    assert len(response.ingredients) == 2
    assert set(response.ingredients) == {"milk", "cheese"}


def test_get_empty_favorites(test_db: Session, family_factory, user_factory):
    """Test getting favorites for user with no favorites."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    service = UserService(test_db)

    response = service.get_favorites(user.id, family.id)
    assert response is not None
    assert response.user_id == user.id
    assert response.total == 0
    assert response.favorites == []


def test_add_favorite_recipe(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test adding a recipe to favorites."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db, name="Pancakes")
    service = UserService(test_db)

    response = service.add_favorite(user.id, family.id, recipe.id)
    assert response is not None
    assert response.user_id == user.id
    assert response.recipe_id == recipe.id
    assert response.recipe_name == "Pancakes"


def test_add_favorite_idempotent(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test that adding same favorite twice is idempotent."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)
    service = UserService(test_db)

    # Add favorite
    response1 = service.add_favorite(user.id, family.id, recipe.id)
    response1_id = response1.id

    # Add same favorite again
    response2 = service.add_favorite(user.id, family.id, recipe.id)

    # Should return same favorite (not create duplicate)
    assert response1_id == response2.id


def test_remove_favorite(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test removing a recipe from favorites."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)
    service = UserService(test_db)

    # Add favorite
    service.add_favorite(user.id, family.id, recipe.id)

    # Remove favorite
    success = service.remove_favorite(user.id, family.id, recipe.id)
    assert success is True

    # Verify removed
    response = service.get_favorites(user.id, family.id)
    assert response.total == 0


def test_remove_favorite_idempotent(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test that removing non-existent favorite is idempotent."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)
    service = UserService(test_db)

    # Remove favorite that doesn't exist
    success = service.remove_favorite(user.id, family.id, recipe.id)
    assert success is True  # Idempotent


def test_is_favorite_returns_true(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test is_favorite returns true for favorite recipe."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)
    service = UserService(test_db)

    service.add_favorite(user.id, family.id, recipe.id)
    is_fav = service.is_favorite(user.id, recipe.id)
    assert is_fav is True


def test_is_favorite_returns_false(test_db: Session, family_factory, user_factory, recipe_factory):
    """Test is_favorite returns false for non-favorite recipe."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)
    service = UserService(test_db)

    is_fav = service.is_favorite(user.id, recipe.id)
    assert is_fav is False
