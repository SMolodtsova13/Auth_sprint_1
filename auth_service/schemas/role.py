from uuid import UUID
from pydantic import BaseModel

from schemas.base import BaseUUID


class RoleCreateDto(BaseModel):
    """Схема создания объекта роли."""

    name: str


class RoleDto(RoleCreateDto, BaseUUID):
    """Схема вывода объекта роли."""

    class Config:
        orm_mode = True


class RoleOperation(BaseModel):
    """Схема объекта роли пользователя."""

    user_id: UUID
    role_id: UUID

    class Config:
        from_attributes = True
