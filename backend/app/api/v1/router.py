"""
V1 API router - aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import recipes, stats, families, users

router = APIRouter()

# Include recipe routes (public, no auth required)
router.include_router(recipes.router)

# Include stats routes (public, no auth required)
router.include_router(stats.router)

# Include family routes (requires authentication)
router.include_router(families.router)

# Include user routes (requires authentication)
router.include_router(users.router)
