from fastapi import APIRouter, Depends, status, Request

from schemas.user import LoginHistoryDto
from services.user import UserService, get_user_service, get_current_user
from models.user import User

router = APIRouter(prefix='/user', tags=['user'])


@router.get(
    '/login-history',
    response_model=list[LoginHistoryDto],
    summary='Вывод истории входов пользователя',
    status_code=status.HTTP_200_OK
)
async def get_user_login_history(
    request: Request,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> list[LoginHistoryDto]:
    """Вывод истории входов пользователя."""
    print(request.headers.get('User-Agent', ''))
    return await user_service.get_user_login_history(user)
