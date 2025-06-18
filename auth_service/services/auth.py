from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt
from models.user import User
from schemas.user import UserCreate
from fastapi import HTTPException, status

MIN_VALUE_PASSWORD = 6


class AuthService:
    @staticmethod
    async def register_user(
        user_create: UserCreate, db: AsyncSession
    ) -> User:
        # Проверка дублирования/пароля
        result = await db.execute(
            select(User).where(User.login == user_create.login)
        )
        if result.scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Пользователь с таким логином уже существует.'
            )

        if len(user_create.password) < MIN_VALUE_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пароль слишком простой (менее 6 символов).'
            )

        # Хешируем пароль
        hashed_password = bcrypt.hash(user_create.password)
        # Создаём объект и сохраняем
        user = User(
            login=user_create.login,
            password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
