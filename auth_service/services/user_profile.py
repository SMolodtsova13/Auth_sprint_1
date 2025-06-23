from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from models.user import User
from schemas.user import ChangeCredentialsRequest


async def change_user_credentials(
    user_id: UUID,
    data: ChangeCredentialsRequest,
    db: AsyncSession
) -> None:
    """Обновляет логин и/или пароль пользователя."""
    # Получаем пользователя из БД
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    # Проверяем текущий пароль
    if not user or not check_password_hash(user.password, data.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный текущий пароль'
        )

    # Обновляем логин и/или пароль
    if data.new_login:
        user.login = data.new_login
    if data.new_password:
        user.password = generate_password_hash(data.new_password)

    # Сохраняем изменения
    db.add(user)
    await db.commit()
