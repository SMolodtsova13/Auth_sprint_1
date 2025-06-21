from http import HTTPStatus

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.role import RoleOperation
from models.role import Role, UserRole


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _is_admin(self, user_id: UUID) -> bool:
        """Проверяет, является ли пользователь администратором."""
        admin_role = await self.db.execute(
            select(Role).where(Role.name == 'admin')
        )
        admin_role = admin_role.scalar_one_or_none()
        if not admin_role:
            return False
        user_role = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == admin_role.id
            )
        )
        return bool(user_role.scalar_one_or_none())

    async def assign_role(self, role_operation: RoleOperation, current_user_id: UUID) -> UserRole:
        # Проверяем права администратора
        if not await self._is_admin(current_user_id):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Только администраторы могут назначать роли'
            )
        # Проверяем существование пользователя и роли
        user = await self._get_user(role_operation.user_id)
        role = await self._get_role(role_operation.role_id)

        # Проверяем, нет ли уже такой роли у пользователя
        existing_role = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == role_operation.user_id,
                UserRole.role_id == role_operation.role_id
            )
        )
        if existing_role.scalar_one_or_none():
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Роль уже назначена пользователю'
            )

        # Создаем новую запись о роли пользователя
        user_role = UserRole(user_id=user.id, role_id=role.id)
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)
        return user_role

    async def remove_role(self, role_operation: RoleOperation, current_user_id: UUID) -> None:
        # Проверяем права администратора
        if not await self._is_admin(current_user_id):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Только администраторы могут удалять роли'
            )
        # Проверяем существование связи пользователь-роль
        user_role = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == role_operation.user_id,
                UserRole.role_id == role_operation.role_id
            )
        )
        user_role = user_role.scalar_one_or_none()
        if not user_role:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Роль не назначена пользователю'
            )

        await self.db.delete(user_role)
        await self.db.commit()
