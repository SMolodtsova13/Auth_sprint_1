from functools import lru_cache

from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.cache import CacheStorage, get_cache_storage
from db.postgres import get_session
from models.user import User, LoginHistory
from services.base import BaseService
from utils.jwt import oauth2_scheme, decode_jwt


class UserService(BaseService):
    """Сервис пользователя."""

    def __init__(self, cache: CacheStorage, *args, **kwargs) -> None:
        self.cache = cache
        super().__init__(*args, **kwargs)

    async def get_user_login_history(
        self, request_user: User
    ) -> list[LoginHistory]:
        """Получение истории входов пользователя."""
        return request_user.login_history

    async def logout_user(
        self, request_user: User, token: str, response: Response
    ) -> None:
        """Выход пользователя из аккаунта"""
        response.delete_cookie(key='access_token')
        response.delete_cookie(key='refresh_token')

        # key = f'invalid_access_token:{request_user.id}'
        # await self.cache.set(key, token, expire)


@lru_cache()
def get_user_service(
    db: AsyncSession = Depends(get_session),
    cache: CacheStorage = Depends(get_cache_storage),
) -> UserService:
    return UserService(db, cache, User)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Метод получения текущего пользователя из токена."""
    payload = decode_jwt(token)
    user_id = payload.get('sub')
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return user
