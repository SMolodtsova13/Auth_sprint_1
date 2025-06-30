from fastapi import (
    APIRouter, Depends, status, Response, Request
)
from fastapi.security import HTTPAuthorizationCredentials

from api.v1.pagination import PaginationParams
from schemas.user import PaginatedLoginHistory
from services.user import UserService, get_user_service, get_current_user
from models.user import User
from utils.jwt import scheme

router = APIRouter(prefix='/user', tags=['user'])


@router.get(
    '/login-history',
    summary='История входов пользователя',
    response_model=PaginatedLoginHistory,
    status_code=status.HTTP_200_OK
)
async def get_login_history(
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    pagination: PaginationParams = Depends()
) -> PaginatedLoginHistory:
    """Вывод истории входов пользователя."""
    return await user_service.get_user_login_history(
        request_user=user,
        pagination=pagination
    )


@router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    summary='Выход пользователя из аккаунта'
)
async def logout_user(
    request: Request,
    response: Response,
    token: HTTPAuthorizationCredentials = Depends(scheme),
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> None:
    """Выход пользователя из аккаунта."""
    await user_service.logout_user(user, token.credentials, request, response)
