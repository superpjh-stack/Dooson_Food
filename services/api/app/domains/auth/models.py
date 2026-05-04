from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class User(BaseModel):
    """사용자 — ADMIN, OPERATOR, QUALITY, VIEWER 역할."""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    # ADMIN | OPERATOR | QUALITY | VIEWER
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="OPERATOR")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
