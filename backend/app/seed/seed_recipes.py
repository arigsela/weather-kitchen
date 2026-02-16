"""
Seed script for loading recipes from JSON into the database.
"""

import json
import sys
import uuid
from pathlib import Path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.recipe import Recipe, RecipeIngredient, RecipeStep, RecipeTag
from app.models.base import DeclarativeBase
from app.config import settings


def load_recipes_from_json(json_path: str) -> list[dict]:
    """Load recipe data from JSON file."""
    with open(json_path, "r") as f:
        return json.load(f)


def seed_recipes(db_session, recipes_data: list[dict]) -> int:
    """
    Seed recipes into database.

    Args:
        db_session: SQLAlchemy session
        recipes_data: List of recipe dictionaries

    Returns:
        Number of recipes seeded
    """
    count = 0

    for recipe_data in recipes_data:
        try:
            # Create recipe
            recipe = Recipe(
                id=uuid.uuid4(),
                name=recipe_data["name"],
                emoji=recipe_data.get("emoji", "🍽️"),
                why=recipe_data.get("why"),
                tip=recipe_data.get("tip"),
                weather=recipe_data.get("weather", "sunny"),
                category=recipe_data.get("category", "lunch"),
                serves=recipe_data.get("serves", 4),
                version_added=recipe_data.get("version_added", "2.0.0"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db_session.add(recipe)
            db_session.flush()  # Flush to get the recipe ID

            # Add ingredients
            for idx, ingredient_text in enumerate(recipe_data.get("ingredients", []), 1):
                ingredient = RecipeIngredient(
                    id=uuid.uuid4(),
                    recipe_id=recipe.id,
                    sort_order=idx,
                    ingredient_text=ingredient_text,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db_session.add(ingredient)

            # Add steps
            for step_number, step_text in enumerate(recipe_data.get("steps", []), 1):
                step = RecipeStep(
                    id=uuid.uuid4(),
                    recipe_id=recipe.id,
                    step_number=step_number,
                    step_text=step_text,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db_session.add(step)

            # Add tags (normalized to lowercase)
            for tag_text in recipe_data.get("tags", []):
                tag = RecipeTag(
                    id=uuid.uuid4(),
                    recipe_id=recipe.id,
                    tag=tag_text.lower(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db_session.add(tag)

            count += 1

            if count % 100 == 0:
                print(f"Seeded {count} recipes...", file=sys.stderr)

        except Exception as e:
            print(f"Error seeding recipe '{recipe_data.get('name')}': {e}", file=sys.stderr)
            db_session.rollback()
            continue

    db_session.commit()
    return count


def main():
    """Main seed script entry point."""
    # Determine seed JSON path
    seed_dir = Path(__file__).parent
    json_path = seed_dir / "data" / "recipes.json"

    if not json_path.exists():
        print(f"Error: Seed JSON not found at {json_path}", file=sys.stderr)
        sys.exit(1)

    # Create database session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()

    try:
        # Load recipe data
        print(f"Loading recipes from {json_path}...", file=sys.stderr)
        recipes_data = load_recipes_from_json(str(json_path))
        print(f"Loaded {len(recipes_data)} recipes from JSON", file=sys.stderr)

        # Seed recipes
        print("Seeding recipes into database...", file=sys.stderr)
        count = seed_recipes(db_session, recipes_data)
        print(f"✓ Successfully seeded {count} recipes!", file=sys.stderr)

    except Exception as e:
        print(f"Error during seeding: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
