from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.user import User, LoginHistory
from services.base import BaseService
from utils.jwt import decode_jwt, oauth2_scheme


class UserService(BaseService):
    """Сервис пользователя."""

    async def get_user_login_history(
        self, request_user: User
    ) -> list[LoginHistory]:
        """Получение истории входов пользователя."""
        return request_user.login_history


@lru_cache()
def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(db, User)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Метод получения текущего пользователя из токена."""
    try:
        payload = decode_jwt(token, verify_exp=True, token_type='access')
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный или истекщий токен'
        )

    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Отсутствует токен'
        )

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    return user
