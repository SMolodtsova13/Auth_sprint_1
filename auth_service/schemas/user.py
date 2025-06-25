from datetime import datetime

from pydantic import BaseModel, constr, model_validator

from core.constants import (
    LOGIN_MAX_LENGTH, LOGIN_MIN_LENGTH,
    PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
)
from schemas.base import BaseUUID


class BaseUser(BaseModel):
    """Базовая схема пользователя."""

    login: constr(
        min_length=LOGIN_MIN_LENGTH,
        max_length=LOGIN_MAX_LENGTH
    )
    password: constr(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH
    )


class UserCreate(BaseUser):
    """Схема для создания нового пользователя."""

    first_name: str
    last_name: str


class SuperUserCreate(UserCreate):
    """Схема для создания суперпользователя."""

    login: str
    password: str


class UserInDB(BaseUUID):
    """Схема возвращаемых данных о пользователе."""

    first_name: str
    last_name: str

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


class ChangeCredentialsRequest(BaseModel):
    """Схема запроса на изменение логина и/или пароля пользователя."""

    new_login: constr(
        min_length=LOGIN_MIN_LENGTH,
        max_length=LOGIN_MAX_LENGTH
    ) | None = None
    new_password: constr(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH
    ) | None = None
    current_password: constr(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH
    )

    @model_validator(mode='after')
    def at_least_one_field(self):
        """Проверка, что указан новый логин или новый пароль."""
        if not self.new_login and not self.new_password:
            raise ValueError('Укажите новый логин или новый пароль')
        return self

 
class LoginHistoryDto(BaseModel):
    """Схема истории входов пользователя."""

    user_agent: str | None
    login_at: datetime

    class Config:
        orm_mode = True
