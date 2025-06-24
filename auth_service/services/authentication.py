from uuid import uuid4
from datetime import datetime

from redis.asyncio import Redis
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import LoginHistory, User
from schemas.user import UserLoginRequest, TokenResponse
from db.redis_db import get_redis
from core.config import settings
from utils.jwt import (
    create_access_token, create_refresh_token, decode_jwt
)


async def authenticate_user(
    data: UserLoginRequest,
    db: AsyncSession,
    request: Request
) -> TokenResponse:
    """Аутентифицирует пользователя по логину и паролю."""
    result = await db.execute(select(User).where(User.login == data.login))
    user = result.scalars().first()

    if not user or not user.check_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль'
        )

    user_id = str(user.id)
    jti = str(uuid4())

    access_token = create_access_token(sub=user_id)
    refresh_token = create_refresh_token(sub=user_id, jti=jti)

    redis = await get_redis()
    key = f'refresh:{user_id}:{jti}'
    await redis.set(
        key,
        refresh_token,
        ex=settings.refresh_token_expire_days * 24 * 3600
    )

    login_rec = LoginHistory(
        user_id=user.id,
        user_agent=str(request.headers.get('User-Agent', '')),
        login_at=datetime.utcnow()
    )
    db.add(login_rec)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


async def handle_refresh_token(token: str, redis: Redis) -> TokenResponse:
    """
    Выполняет валидацию refresh-токена и генерирует новый access и refresh токены.
    """
    # Проверяем токен
    payload = decode_jwt(token, verify_exp=True, token_type='refresh')
    user_id = payload.get('sub')
    jti = payload.get('jti')

    if not user_id or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен'
        )

    # Проверяем наличие в Redis
    key = f'refresh:{user_id}:{jti}'
    stored_token = await redis.get(key)

    if stored_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh-токен недействителен или уже отозван'
        )

    # Удаляем старый refresh
    await redis.delete(key)

    # Генерируем новые токены
    new_jti = str(uuid4())
    new_refresh_token = create_refresh_token(sub=user_id, jti=new_jti)
    new_access_token = create_access_token(sub=user_id)

    # Сохраняем новый refresh-токен
    new_key = f'refresh:{user_id}:{new_jti}'
    await redis.set(
        new_key,
        new_refresh_token,
        ex=settings.refresh_token_expire_days * 24 * 3600
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
