"""
V1 API router - aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import recipes, stats

router = APIRouter()

# Include recipe routes (public, no auth required)
router.include_router(recipes.router)

# Include stats routes (public, no auth required)
router.include_router(stats.router)

# Future routers will be added here:
# - router.include_router(families.router)
# - router.include_router(users.router)
# - router.include_router(auth.router)
