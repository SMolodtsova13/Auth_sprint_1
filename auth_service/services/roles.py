from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from db.postgres import get_session
from models.role import Role, UserRole
from services.base import BaseService
from schemas.role import RoleOperation, RoleDto


class RoleService(BaseService):
    """Сервис ролей."""

    async def _get_role(self, obj_id: UUID) -> Role:
        """Получение объекта роли."""
        role_obj = await self.get_by_id(obj_id)
        if not role_obj:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Объект не найден.'
            )
        return role_obj

    async def _check_role_name(self, name: str) -> None:
        """Проверка сущестования роли по названию."""
        if await self.get_by_kwargs(name=name):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Роль {name} - уже существует.'
            )

    async def _check_protected_role(self, obj: Role) -> None:
        """Проверка защищенных от удаления ролей."""
        if obj.name == 'superuser':
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Роль superuser защищена от удаления.'
            )

    async def create_role(self, request_obj: RoleDto) -> Role:
        """Создание объекта роли."""
        await self._check_role_name(name=request_obj.name)
        return await self.create(request_obj)

    async def update_role(self, request_obj: RoleDto, role_id: UUID) -> Role:
        """Обновление объекта роли."""
        role_obj = await self._get_role(role_id)
        return await self.update(role_obj, request_obj)

    async def delete_role(self, role_id: UUID) -> None:
        """Удаление объекта роли."""
        role_obj = await self._get_role(role_id)
        await self._check_protected_role(role_obj)
        return await self.delete(role_obj)

    async def get_roles_list(self) -> list[Role]:
        """Получение списка существующих ролей."""
        return await self.get_all()


@lru_cache()
def get_role_service(
    db: AsyncSession = Depends(get_session)
) -> RoleService:
    return RoleService(db, Role)


class UserRoleService:
    """Сервис роли пользователя."""

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
