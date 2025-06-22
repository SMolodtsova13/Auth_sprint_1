from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from schemas.user import UserCreate
from core.constants import PASSWORD_MIN_LENGTH


class AuthService:
    """Сервис для регистрации пользователей."""

    @staticmethod
    async def register_user(
        user_create: UserCreate, db: AsyncSession
    ) -> User:
        """
        Регистрирует нового пользователя.
        Хеширование происходит в модели User.__init__.
        """
        # Проверка дублирования/пароля
        result = await db.execute(
            select(User).where(User.login == user_create.login)
        )
        if result.scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Пользователь с таким логином уже существует.'
            )

        if len(user_create.password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль слишком простой (менее 6 символов).'
            )

        # Передаём сырой пароль — модель хеширует
        # Создаём объект и сохраняем
        user = User(
            login=user_create.login,
            password=user_create.password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
