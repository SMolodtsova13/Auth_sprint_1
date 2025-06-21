from uuid import uuid4
from datetime import datetime

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import LoginHistory, User
from schemas.user import UserLoginRequest, TokenResponse
from services.jwt_utils import create_access_token, create_refresh_token
from db.redis_db import get_redis
from core.config import settings


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

    # Получаем роли пользователя
    # roles = [role.name for role in user.roles]

    access_token = create_access_token(
        sub=user_id,
        # roles=roles
    )
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
        user_agent=request.headers.get('User-Agent', ''),
        login_at=datetime.utcnow()
    )
    db.add(login_rec)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
