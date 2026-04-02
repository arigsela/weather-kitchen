"""
Authentication endpoints: token refresh and logout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SuccessResponse,
    TokenResponse,
)
from app.schemas.family import FamilyCreateResponse
from app.services.family_service import FamilyService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=FamilyCreateResponse,
    summary="Login",
    description="Authenticate with family name and password. Returns JWT tokens.",
)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> FamilyCreateResponse:
    """Login with family name and password."""
    if settings.beta_access_code and request.beta_code != settings.beta_access_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid beta access code",
        )

    service = FamilyService(db)

    try:
        result = service.login(name=request.name, password=request.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid family name or password",
        )

    family_response, access_token, refresh_token = result
    return FamilyCreateResponse(
        id=family_response.id,
        name=family_response.name,
        family_size=family_response.family_size,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access + refresh token pair.",
)
async def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Issue new token pair using a valid refresh token (rotates the refresh token)."""
    service = FamilyService(db)
    result = service.refresh_access_token(request.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, new_refresh_token = result
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",  # noqa: S106
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logout",
    description="Revoke the provided refresh token, effectively logging out the session.",
)
async def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Revoke a refresh token."""
    service = FamilyService(db)
    service.logout(request.refresh_token)
    # Always return success to avoid token enumeration
    return SuccessResponse(success=True, message="Logged out successfully")
