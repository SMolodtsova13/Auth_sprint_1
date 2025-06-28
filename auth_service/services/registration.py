from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import PASSWORD_MIN_LENGTH
from db.postgres import get_session
from models.user import User
from schemas.user import UserCreate
from services.base import BaseService


class AuthService(BaseService):
    """Сервис для регистрации пользователей."""

    async def register_user(self, user_create: UserCreate) -> User:
        """
        Регистрирует нового пользователя.
        Хеширование происходит в модели User.__init__.
        """
        if await self.db.get_by_kwargs(login=user_create.login):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Пользователь с таким логином уже существует.'
            )

        if len(user_create.password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль слишком простой (менее 6 символов).'
            )
        return await self.db.create(user_create)


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(db, User)
