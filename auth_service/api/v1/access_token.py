from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from core.config import settings
from services.jwt_utils import (
    create_access_token, create_refresh_token, decode_jwt
)
from schemas.user import TokenResponse
from db.redis_db import get_redis

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis)
) -> TokenResponse:
    """
    Обновление access-токена по refresh-токену.
    """
    # Декодируем и проверяем тип
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
