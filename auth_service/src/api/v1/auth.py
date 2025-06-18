from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserInDB, UserLoginRequest, TokenResponse
from auth_service.src.services.registration import AuthService
from db.postgres import get_session
from services.auth.authentication import authenticate_user

router = APIRouter(prefix='/auth', tags=['auth'])
# router = APIRouter()


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

# @router.post('/login', response_model=TokenResponse)
# async def login(
#     login_data: UserLoginRequest,
#     session: AsyncSession = Depends(get_session),
# ):
#     return await authenticate_user(login_data, session)
