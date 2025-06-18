from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from src.models.user import User
from src.schemas.user import UserLoginRequest
from src.core.config import settings
from src.services.auth.jwt_utils import create_tokens
from werkzeug.security import check_password_hash


async def authenticate_user(
    login_data: UserLoginRequest, session: AsyncSession
) -> dict:
    stmt = select(User).where(User.login == login_data.login)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user or not user.check_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль'
        )

    return create_tokens(user_id=str(user.id))
