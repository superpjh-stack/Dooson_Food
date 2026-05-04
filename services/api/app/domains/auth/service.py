import logging
import uuid
from datetime import datetime, timedelta, UTC

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.domains.auth.models import User
from app.domains.auth.schemas import UserCreate, UserResponse
from app.shared.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Password helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _hash_password(plain: str) -> str:
        return _pwd_context.hash(plain)

    @staticmethod
    def _verify_password(plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

    # ── User CRUD ─────────────────────────────────────────────────────────────

    async def create_user(self, data: UserCreate) -> UserResponse:
        # Check duplicate username / email
        existing = await self.db.execute(
            select(User).where(
                (User.username == data.username) | (User.email == data.email)
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ValidationException("이미 사용 중인 사용자명 또는 이메일입니다")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=self._hash_password(data.password),
            role=data.role,
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        logger.info(f"[AUTH] User created: {user.username} role={user.role}")
        return UserResponse.model_validate(user)

    async def authenticate(self, username: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"[AUTH] Login failed: user not found username={username}")
            return None
        if not user.is_active:
            logger.warning(f"[AUTH] Login failed: account inactive username={username}")
            return None
        if not self._verify_password(password, user.hashed_password):
            logger.warning(f"[AUTH] Login failed: wrong password username={username}")
            return None
        logger.info(f"[AUTH] Login success: {username} role={user.role}")
        return user

    def create_access_token(self, user: User) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": expire,
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
        logger.info(f"[AUTH] Token issued: {user.username} expires={expire.isoformat()}")
        return token

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise ValidationException("유효하지 않은 토큰입니다")
        except JWTError as exc:
            raise ValidationException(f"토큰 검증 실패: {exc}") from exc

        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise NotFoundException("사용자를 찾을 수 없습니다")
        return user
