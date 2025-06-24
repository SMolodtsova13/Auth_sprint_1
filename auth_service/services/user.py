from functools import lru_cache

from fastapi import Security, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.user import User, LoginHistory
from services.base import BaseService
from utils.jwt import decode_jwt

security = HTTPBearer()
api_key_header = APIKeyHeader(name="Authorization", scheme_name="BearerAuth")


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


# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Security(security),
#     # credentials: HTTPAuthorizationCredentials = Depends(security),
#     user_service: UserService = Depends(get_user_service)
# ) -> User:
#     """Метод получения текущего пользователя из токена."""
#     token = credentials.credentials
#     payload = decode_jwt(token)
#     user_id = payload['sub']
#     user = await user_service.get_by_id(user_id)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Пользователь не найден',
#         )
#     return user

async def get_current_user(
    authorization: str = Security(api_key_header),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Метод получения текущего пользователя из токена."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный формат авторизации'
        )
    token = authorization.split(' ', 1)[1]
    payload = decode_jwt(token)
    user_id = payload['sub']
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    return user
