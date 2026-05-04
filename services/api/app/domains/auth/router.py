import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.auth.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.domains.auth.service import AuthService
from app.infrastructure.auth import get_current_user
from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["인증/권한"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    logger.info(f"[API] POST /auth/register username={payload.username}")
    return await service.create_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    logger.info(f"[API] POST /auth/login username={payload.username}")
    user = await service.authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = service.create_access_token(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    logger.info(f"[API] GET /auth/me username={current_user.username}")
    return UserResponse.model_validate(current_user)
