"""
Common schema definitions used across the API.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detail about a specific validation error."""

    field: str | None = Field(None, description="Field name that caused the error")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    code: str = Field(..., description="Error code (e.g., VALIDATION_ERROR)")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(None, description="Field-level error details")

    model_config = ConfigDict(examples=[
        {
            "code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": [
                {"field": "family_size", "message": "Must be between 1 and 20"}
            ],
        }
    ])


class PaginationParams(BaseModel):
    """Pagination query parameters for list endpoints."""

    limit: int = Field(20, ge=1, le=100, description="Items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")

    model_config = ConfigDict(examples=[
        {"limit": 20, "offset": 0},
        {"limit": 50, "offset": 100},
    ])


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    total: int = Field(..., description="Total number of items available")
    limit: int = Field(..., description="Items returned per page")
    offset: int = Field(..., description="Number of items skipped")
    items: list[T] = Field(..., description="List of items")

    @property
    def has_next(self) -> bool:
        """Check if there are more items."""
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Check if there are previous items."""
        return self.offset > 0
