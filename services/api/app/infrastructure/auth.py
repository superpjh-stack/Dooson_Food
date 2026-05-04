import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """FastAPI dependency — decode JWT and return the authenticated User."""
    from app.domains.auth.models import User
    from app.domains.auth.service import AuthService

    token = credentials.credentials
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return user


def require_role(*roles: str):
    """Factory — returns a FastAPI dependency that enforces role membership.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(user = Depends(require_role("ADMIN"))):
            ...
    """
    async def _check(
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"이 작업에는 {'/'.join(roles)} 권한이 필요합니다",
            )
        return current_user

    return _check
