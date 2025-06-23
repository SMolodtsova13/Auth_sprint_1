from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from db.postgres import get_session
from models.user import User, LoginHistory
from services.base import BaseService
from utils.jwt import oauth2_scheme, decode_jwt


class UserService(BaseService):
    """Сервис пользователя."""

    async def get_user_login_history(
        self, request_user: User
    ) -> list[LoginHistory]:
        """Получение истории входов пользователя."""
        print(request_user.login_history)
        print(type(request_user.login_history))
        return request_user.login_history


@lru_cache()
def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(db, User)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Метод получения текущего пользователя из токена."""
    payload = decode_jwt(token)
    user_id = payload['sub']
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return user
