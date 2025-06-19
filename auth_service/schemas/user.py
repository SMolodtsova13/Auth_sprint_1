from uuid import UUID

from pydantic import BaseModel, constr

from core.constants import (
    LOGIN_MAX_LENGTH, LOGIN_MIN_LENGTH, PASSWORD_MIN_LENGTH
)


class BaseUser(BaseModel):
    login: constr(
        min_length=LOGIN_MIN_LENGTH,
        max_length=LOGIN_MAX_LENGTH
    )
    password: constr(min_length=PASSWORD_MIN_LENGTH)


class UserCreate(BaseUser):
    """Схема для создания нового пользователя."""
    first_name: str
    last_name: str


class SuperUserCreate(BaseModel):

    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    """Схема возвращаемых данных о пользователе."""
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class RoleOperation(BaseModel):
    user_id: UUID
    role_id: UUID

    class Config:
        from_attributes = True


class UserLoginRequest(BaseUser):
    """Схема запроса для входа пользователя."""
    pass


class TokenResponse(BaseModel):
    """Схема возвращаемого ответа с JWT токенами."""
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
