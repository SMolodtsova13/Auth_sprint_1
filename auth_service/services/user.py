from functools import lru_cache

from fastapi import Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.config import settings
from db.cache import CacheStorage, get_cache_storage
from db.postgres import get_session
from models.user import User, LoginHistory
from services.base import BaseService
from utils.jwt import decode_jwt, scheme
from schemas.user import PaginatedLoginHistory, LoginHistoryDto


class UserService(BaseService):
    """Сервис пользователя."""

    def __init__(self, cache: CacheStorage, *args, **kwargs) -> None:
        self.cache = cache
        super().__init__(*args, **kwargs)

    async def get_user_login_history(
        self, request_user: User, page: int = 1, size: int = 10
    ) -> PaginatedLoginHistory:
        """Получение истории входов пользователя."""
        offset = (page - 1) * size

        # используем self.db_session — это AsyncSession
        total_stmt = select(func.count(LoginHistory.id)).where(
                LoginHistory.user_id == request_user.id
            )
        total_result = await self.db_session.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(LoginHistory)
            .where(LoginHistory.user_id == request_user.id)
            .order_by(LoginHistory.login_at.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.db_session.execute(stmt)
        items = result.scalars().all()

        return PaginatedLoginHistory(
            total=total,
            page=page,
            size=size,
            items=[LoginHistoryDto.from_orm(item) for item in items]
        )

    async def logout_user(
        self,
        request_user: User,
        token: str,
        request: Request,
        response: Response
    ) -> None:
        """Выход пользователя из аккаунта."""
        response.delete_cookie(key='Authorization')
        response.delete_cookie(key='refresh_token')
        user_agent = str(request.headers.get('User-Agent', ''))
        key = f'refresh:{request_user.id}:{user_agent}'
        if await self.cache.get(key):
            await self.cache.delete(key)
        key = f'invalid_access_token:{request_user.id}:{token}'
        await self.cache.set(key, token, settings.access_token_expire_seconds)


@lru_cache()
def get_user_service(
    cache: CacheStorage = Depends(get_cache_storage),
    db: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(cache, db, User)


async def get_current_user(
    token_credentials: HTTPAuthorizationCredentials = Depends(scheme),
    cache: CacheStorage = Depends(get_cache_storage),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Метод получения текущего пользователя из токена."""
    token = token_credentials.credentials
    payload = decode_jwt(token, token_type='access')
    user_id = payload['sub']

    user = await user_service.get_obj_or_404(user_id)
    if await cache.get(f'invalid_access_token:{user_id}:{token}'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен недействителен'
        )
    return user
