"""
Family management endpoints - create, read, update, delete families and manage authentication.
"""

import json
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.family import Family
from app.services.family_service import FamilyService
from app.services.audit_service import _audit_log_background
from app.schemas.family import (
    FamilyCreate, FamilyCreateResponse, FamilyResponse, FamilyUpdate, FamilyExportResponse
)
from app.schemas.auth import (
    TokenRotateRequest, TokenRotateResponse, PinVerifyRequest, PinVerifyResponse,
    SuccessResponse,
)
from app.config import settings
from app.auth.dependencies import get_current_family, require_family_owner, require_pin
from app.middleware.request_id import get_request_id

router = APIRouter(prefix="/api/v1", tags=["families"])


@router.post(
    "/families",
    response_model=FamilyCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create family account",
    description="Create new family with admin PIN. Returns one-time plaintext API token.",
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
        admin_pin=request.admin_pin,
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
        token_type="bearer",
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
    description="Permanently delete family account (requires authentication + PIN)",
)
async def hard_delete_family(
    family_id: UUID,
    request: PinVerifyRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> SuccessResponse:
    """Hard delete family (permanent deletion after PIN verification)."""
    # Verify PIN
    verified, _ = FamilyService(db).verify_pin(family_id, request.admin_pin)
    if not verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")

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
    description="Generate new API token and invalidate old (requires authentication + PIN)",
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
    """Rotate API token after PIN verification."""
    # Verify PIN
    service = FamilyService(db)
    verified, _ = service.verify_pin(family_id, request.admin_pin)
    if not verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")

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
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/families/{family_id}/verify-pin",
    response_model=PinVerifyResponse,
    summary="Verify PIN",
    description="Verify admin PIN (requires authentication)",
)
async def verify_pin(
    family_id: UUID,
    request: PinVerifyRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PinVerifyResponse:
    """Verify admin PIN."""
    service = FamilyService(db)
    success, message = service.verify_pin(family_id, request.admin_pin)

    if success:
        background_tasks.add_task(
            _audit_log_background,
            action="pin.verified",
            entity_type="auth",
            entity_id=family_id,
            ip=http_request.client.host,
            family_id=family_id,
            user_agent=http_request.headers.get("user-agent"),
        )
        return PinVerifyResponse(success=True, message="PIN verified successfully")
    else:
        background_tasks.add_task(
            _audit_log_background,
            action="pin.failed",
            entity_type="auth",
            entity_id=family_id,
            ip=http_request.client.host,
            family_id=family_id,
            user_agent=http_request.headers.get("user-agent"),
            details=json.dumps({"reason": message}),
        )
        return PinVerifyResponse(success=False, message=message or "Invalid PIN")
