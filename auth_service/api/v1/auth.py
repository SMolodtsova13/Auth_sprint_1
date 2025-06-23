from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from schemas.user import UserCreate, UserLoginRequest, UserInDB, TokenResponse
from services.registration import AuthService
from services.authentication import authenticate_user, handle_refresh_token
from db.postgres import get_session
from db.redis_db import get_redis
from utils.jwt import oauth2_scheme

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
        '/register',
        response_model=UserInDB,
        status_code=status.HTTP_201_CREATED,
        summary='Регистрация пользователя'
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    """Регистрирует нового пользователя."""
    return await AuthService.register_user(user_create, db)


@router.post(
        '/login',
        response_model=TokenResponse,
        status_code=status.HTTP_200_OK,
        summary='Аутентификация пользователя'
)
async def login(
    login_data: UserLoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Аутентификация пользователя. """
    return await authenticate_user(login_data, session, request)


@router.post(
    '/refresh',
    response_model=TokenResponse,
    summary='Обновление access-токена'
)
async def refresh_token(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis)
) -> TokenResponse:
    """
    Обновление access-токена по refresh-токену.
    """
    return await handle_refresh_token(token, redis)
