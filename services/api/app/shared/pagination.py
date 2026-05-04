from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: dict

    @classmethod
    def create(cls, items: list[T], total: int, params: PaginationParams):
        return cls(
            data=items,
            pagination={
                "page": params.page,
                "limit": params.limit,
                "total": total,
                "total_pages": -(-total // params.limit),  # ceiling division
            },
        )
