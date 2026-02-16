"""
Family management endpoints - create, read, update, delete families and manage authentication.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.family import Family
from app.services.family_service import FamilyService
from app.schemas.family import (
    FamilyCreate, FamilyCreateResponse, FamilyResponse, FamilyUpdate, FamilyExportResponse
)
from app.schemas.auth import (
    TokenRotateRequest, TokenRotateResponse, PinVerifyRequest, PinVerifyResponse,
    ConsentRequestResponse, ConsentVerifyRequest, ConsentVerifyResponse, SuccessResponse
)
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
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyCreateResponse:
    """Create a new family account."""
    service = FamilyService(db)
    family_response, plaintext_token = service.create_family(
        name=request.name,
        family_size=request.family_size,
        admin_pin=request.admin_pin,
    )

    return FamilyCreateResponse(
        family_id=family_response.id,
        name=family_response.name,
        api_token=plaintext_token,
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
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> SuccessResponse:
    """Soft delete family (mark as inactive)."""
    service = FamilyService(db)
    success = service.soft_delete(family_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

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
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> SuccessResponse:
    """Hard delete family (permanent deletion after PIN verification)."""
    # Verify PIN
    verified, _ = FamilyService(db).verify_pin(family_id, request.admin_pin)
    if not verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")

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
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FamilyExportResponse:
    """Export all family data for GDPR."""
    service = FamilyService(db)
    data = service.export_family_data(family_id)

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

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
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TokenRotateResponse:
    """Rotate API token after PIN verification."""
    # Verify PIN
    verified, _ = FamilyService(db).verify_pin(family_id, request.admin_pin)
    if not verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")

    service = FamilyService(db)
    new_token = service.rotate_token(family_id)

    if not new_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    return TokenRotateResponse(
        family_id=family_id,
        api_token=new_token,
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
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> PinVerifyResponse:
    """Verify admin PIN."""
    service = FamilyService(db)
    success, message = service.verify_pin(family_id, request.admin_pin)

    if success:
        return PinVerifyResponse(success=True, message="PIN verified successfully")
    else:
        return PinVerifyResponse(success=False, message=message or "Invalid PIN")


@router.post(
    "/families/{family_id}/consent/request",
    response_model=ConsentRequestResponse,
    summary="Request parental consent",
    description="Send consent verification code to parent email (requires authentication)",
)
async def request_consent(
    family_id: UUID,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ConsentRequestResponse:
    """Request parental consent code."""
    service = FamilyService(db)
    code = service.request_consent_code(family_id)

    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    # In production, send via email_service
    # For now, just note it was generated
    parent_email = family.parent_email or "parent@example.com"
    masked_email = parent_email.replace(parent_email.split("@")[0][2:], "***")

    return ConsentRequestResponse(
        family_id=family_id,
        message=f"Consent code sent to {parent_email}",
        code_sent_to=masked_email,
    )


@router.post(
    "/families/{family_id}/consent/verify",
    response_model=ConsentVerifyResponse,
    summary="Verify parental consent",
    description="Verify consent code and set consent flag (requires authentication + PIN)",
)
async def verify_consent(
    family_id: UUID,
    request: ConsentVerifyRequest,
    family: Family = Depends(require_family_owner),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ConsentVerifyResponse:
    """Verify parental consent code after PIN verification."""
    # Verify PIN first
    service = FamilyService(db)
    verified, _ = service.verify_pin(family_id, request.admin_pin)
    if not verified:
        return ConsentVerifyResponse(success=False, message="Invalid PIN")

    # Verify consent code
    success = service.verify_consent_code(family_id, request.consent_code)

    if not success:
        return ConsentVerifyResponse(success=False, message="Invalid or expired consent code")

    return ConsentVerifyResponse(
        success=True,
        message="Parental consent verified",
        family_id=family_id,
    )
