"""
Family management endpoints - create, read, update, delete families and manage authentication.
"""

import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_family_owner
from app.config import settings
from app.database import get_db
from app.middleware.request_id import get_request_id
from app.models.family import Family
from app.schemas.auth import (
    PasswordVerifyRequest,
    PasswordVerifyResponse,
    SuccessResponse,
    TokenRotateRequest,
    TokenRotateResponse,
)
from app.schemas.family import (
    FamilyCreate,
    FamilyCreateResponse,
    FamilyExportResponse,
    FamilyResponse,
    FamilyUpdate,
)
from app.services.audit_service import _audit_log_background
from app.services.family_service import FamilyService

router = APIRouter(prefix="/api/v1", tags=["families"])


@router.post(
    "/families",
    response_model=FamilyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create family account",
    description="Create new family with password. Returns JWT tokens.",
)
async def create_family(
    request: FamilyCreate,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyCreateResponse:
    """Create a new family account."""
    service = FamilyService(db)
    family_response, access_token, refresh_token = service.create_family(
        name=request.name,
        family_size=request.family_size,
        password=request.password,
    )

    background_tasks.add_task(
        _audit_log_background,
        action="family.created",
        entity_type="family",
        entity_id=family_response.id,
        ip=http_request.client.host,
        family_id=family_response.id,
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"family_name": request.name, "family_size": request.family_size}),
    )

    return FamilyCreateResponse(
        id=family_response.id,
        name=family_response.name,
        family_size=family_response.family_size,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
    "/families/{family_id}",
    response_model=FamilyResponse,
    summary="Get family details",
    description="Get family account details (requires authentication)",
)
async def get_family(
    family_id: UUID,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyResponse:
    """Get family details (requires valid API token)."""
    return FamilyResponse.model_validate(family)


@router.put(
    "/families/{family_id}",
    response_model=FamilyResponse,
    summary="Update family settings",
    description="Update family name or size (requires authentication)",
)
async def update_family(
    family_id: UUID,
    request: FamilyUpdate,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyResponse:
    """Update family settings (requires valid API token)."""
    service = FamilyService(db)
    updated = service.update_family(
        family_id,
        name=request.name,
        family_size=request.family_size,
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    return updated


@router.delete(
    "/families/{family_id}",
    response_model=SuccessResponse,
    summary="Soft delete family",
    description="Soft delete family account (can be recovered) (requires authentication)",
)
async def soft_delete_family(
    family_id: UUID,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> SuccessResponse:
    """Soft delete family (mark as inactive)."""
    service = FamilyService(db)
    success = service.soft_delete(family_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    background_tasks.add_task(
        _audit_log_background,
        action="family.soft_deleted",
        entity_type="family",
        entity_id=family_id,
        ip=http_request.client.host,
        family_id=family_id,
        user_agent=http_request.headers.get("user-agent"),
    )

    return SuccessResponse(success=True, message="Family soft-deleted successfully")


@router.post(
    "/families/{family_id}/purge",
    response_model=SuccessResponse,
    summary="Hard delete family",
    description="Permanently delete family account (requires authentication + password)",
)
async def hard_delete_family(
    family_id: UUID,
    request: PasswordVerifyRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> SuccessResponse:
    """Hard delete family (permanent deletion after password verification)."""
    from app.auth.password import verify_password

    if not family.password_hash or not verify_password(request.password, family.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    # Log before deleting so the family_id FK still resolves in the background session.
    # AuditLog has ON DELETE CASCADE so the entry will be removed with the family, but
    # the background task opening its own session may race; log before hard-delete runs.
    background_tasks.add_task(
        _audit_log_background,
        action="family.hard_deleted",
        entity_type="family",
        entity_id=family_id,
        ip=http_request.client.host,
        family_id=None,  # avoid FK violation after hard delete
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"family_id": str(family_id)}),
    )

    service = FamilyService(db)
    success = service.hard_delete(family_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    return SuccessResponse(success=True, message="Family permanently deleted")


@router.get(
    "/families/{family_id}/export",
    response_model=FamilyExportResponse,
    summary="Export family data",
    description="Export all family data for GDPR compliance (requires authentication)",
)
async def export_family(
    family_id: UUID,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyExportResponse:
    """Export all family data for GDPR."""
    service = FamilyService(db)
    data = service.export_family_data(family_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    background_tasks.add_task(
        _audit_log_background,
        action="family.exported",
        entity_type="family",
        entity_id=family_id,
        ip=http_request.client.host,
        family_id=family_id,
        user_agent=http_request.headers.get("user-agent"),
    )

    return FamilyExportResponse(**data)


@router.post(
    "/families/{family_id}/token/rotate",
    response_model=TokenRotateResponse,
    summary="Rotate API token",
    description="Generate new API token and invalidate old (requires authentication + password)",
)
async def rotate_token(
    family_id: UUID,
    request: TokenRotateRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TokenRotateResponse:
    """Rotate API token after password verification."""
    from app.auth.password import verify_password

    if not family.password_hash or not verify_password(request.password, family.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    service = FamilyService(db)

    access_token, refresh_token = service.rotate_tokens(family_id)

    background_tasks.add_task(
        _audit_log_background,
        action="token.rotated",
        entity_type="auth",
        entity_id=family_id,
        ip=http_request.client.host,
        family_id=family_id,
        user_agent=http_request.headers.get("user-agent"),
    )

    return TokenRotateResponse(
        family_id=family_id,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/families/{family_id}/verify-password",
    response_model=PasswordVerifyResponse,
    summary="Verify password",
    description="Verify family password (requires authentication)",
)
async def verify_password_endpoint(
    family_id: UUID,
    request: PasswordVerifyRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PasswordVerifyResponse:
    """Verify family password."""
    from app.auth.password import verify_password

    success = bool(family.password_hash and verify_password(request.password, family.password_hash))

    if success:
        background_tasks.add_task(
            _audit_log_background,
            action="password.verified",
            entity_type="auth",
            entity_id=family_id,
            ip=http_request.client.host,
            family_id=family_id,
            user_agent=http_request.headers.get("user-agent"),
        )
        return PasswordVerifyResponse(success=True, message="Password verified")
    else:
        background_tasks.add_task(
            _audit_log_background,
            action="password.failed",
            entity_type="auth",
            entity_id=family_id,
            ip=http_request.client.host,
            family_id=family_id,
            user_agent=http_request.headers.get("user-agent"),
        )
        return PasswordVerifyResponse(success=False, message="Invalid password")
