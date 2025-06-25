from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User
from schemas.user import ChangeCredentialsRequest
from core.constants import (
    LOGIN_MAX_LENGTH, LOGIN_MIN_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
)


async def change_user_credentials(
    user_id: UUID,
    data: ChangeCredentialsRequest,
    db: AsyncSession
) -> None:
    """Обновляет логин и/или пароль пользователя."""

    # Получаем пользователя из БД
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user or not check_password_hash(
        user.password,
        data.current_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный текущий пароль'
        )

    # Обновляем логин и/или пароль
    if data.new_login:
        if not (LOGIN_MIN_LENGTH <= len(data.new_login) <= LOGIN_MAX_LENGTH):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Логин должен быть от {LOGIN_MIN_LENGTH} до {LOGIN_MAX_LENGTH} символов'
            )

        if data.new_login != user.login:
            existing = await db.execute(
                select(User).where(User.login == data.new_login)
            )
            existing_user = existing.scalars().first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='Пользователь с таким логином уже существует'
                )

            user.login = data.new_login

    # Проверка и обновление пароля
    if data.new_password:
        if not (
            PASSWORD_MIN_LENGTH <= len(data.new_password) <= PASSWORD_MAX_LENGTH
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Пароль должен быть от {PASSWORD_MIN_LENGTH} до {PASSWORD_MAX_LENGTH} символов'
            )
        user.password = generate_password_hash(data.new_password)

    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким логином уже существует'
        )
