from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.entity import UserCreate, UserInDB
from services.auth import AuthService
from db.postgres import get_session

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
        '/register',
        response_model=UserInDB,
        status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    return await AuthService.register_user(user_create, db)
