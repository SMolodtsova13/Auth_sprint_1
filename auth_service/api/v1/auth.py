from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserInDB, UserLoginRequest, TokenResponse
from services.registration import AuthService
from db.postgres import get_session
from services.authentication import authenticate_user


router = APIRouter()


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
