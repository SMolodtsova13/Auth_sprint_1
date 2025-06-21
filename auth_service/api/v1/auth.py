from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserLoginRequest, UserInDB, TokenResponse
from services.registration import AuthService
from services.authentication import authenticate_user
from db.postgres import get_session

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
