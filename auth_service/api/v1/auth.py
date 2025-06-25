from fastapi import Depends, APIRouter, status, Request
from fastapi.security import (
    HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
)
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from models.user import User
from schemas.user import (
    UserCreate, UserLoginRequest, UserInDB,
    TokenResponse, ChangeCredentialsRequest
)
from services.user import get_current_user
from services.registration import AuthService
from services.user_profile import change_user_credentials
from services.authentication import authenticate_user, handle_refresh_token
from db.postgres import get_session
from db.redis_db import get_redis


refresh_scheme = HTTPBearer()

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
    request: Request,
    session: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Аутентификация пользователя. """
    login_data = UserLoginRequest(
        login=form_data.username,
        password=form_data.password
    )
    return await authenticate_user(login_data, session, request)


@router.post(
    '/refresh',
    response_model=TokenResponse,
    summary='Обновление токенов'
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(refresh_scheme),
    redis: Redis = Depends(get_redis),
) -> TokenResponse:
    """
    Принимает refresh-токен в Authorization: Bearer <token>.
    Возвращает новую пару токенов для того же device_id.
    """
    token = credentials.credentials
    return await handle_refresh_token(token, redis)


@router.post(
    '/me/change',
    status_code=status.HTTP_200_OK,
    summary='Изменение логина или пароля пользователя'
)
async def change_credentials(
    data: ChangeCredentialsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Изменение логина и/или пароля текущего пользователя."""
    await change_user_credentials(user_id=current_user.id, data=data, db=db)
    return {'message': 'Данные успешно изменены'}
