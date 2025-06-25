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
    """
    Аутентифицирует пользователя по логину и паролю.
    Создаёт пару токенов для нового устройства.
    """
    result = await db.execute(select(User).where(User.login == data.login))
    user = result.scalars().first()

    if not user or not user.check_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль'
        )

    user_id = str(user.id)
    # Генерация уникального device_id для сессии
    device_id = str(uuid4())

    access_token = create_access_token(sub=user_id, device_id=device_id)
    refresh_token = create_refresh_token(sub=user_id, device_id=device_id)

    redis: Redis = await get_redis()
    key = f'refresh:{user_id}:{device_id}'
    await redis.set(
        key,
        refresh_token,
        ex=settings.refresh_token_expire_days * 24 * 3600
    )

    # Сохраняем историю входа
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
    """Выполняет валидацию refresh-токена, обновляет пару токенов."""
    # Проверяем токен
    payload = decode_jwt(token, verify_exp=True, token_type='refresh')
    user_id = payload.get('sub')
    device_id = payload.get('device_id')

    if not user_id or not device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен'
        )

    # Проверяем наличие в Redis
    key = f'refresh:{user_id}:{device_id}'
    stored_token = await redis.get(key)

    if stored_token != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh-токен недействителен или уже отозван'
        )

    # Удаляем старый refresh-токен
    await redis.delete(key)

    # Генерируем новую пару токенов с новым device_id
    new_device_id = str(uuid4())
    new_refresh_token = create_refresh_token(sub=user_id, device_id=new_device_id)
    new_access_token = create_access_token(sub=user_id, device_id=new_device_id)

    # Сохраняем новый refresh-токен
    new_key = f'refresh:{user_id}:{new_device_id}'
    await redis.set(
        new_key,
        new_refresh_token,
        ex=settings.refresh_token_expire_days * 24 * 3600
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
