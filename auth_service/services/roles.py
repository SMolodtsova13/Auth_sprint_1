from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.postgres import get_session
from models.role import Role, UserRole
from services.base import BaseService
from schemas.role import RoleOperation, RoleDto
from models.user import User
from utils.role import permission_required


class RoleService(BaseService):
    """Сервис ролей."""

    async def _check_role_name(self, name: str) -> None:
        """Проверка сущестования роли по названию."""
        if await self.db.get_by_kwargs(name=name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Роль {name} - уже существует.'
            )

    async def _check_protected_role(self, obj: Role) -> None:
        """Проверка защищенных от удаления ролей."""
        if obj.name == 'superuser':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Роль superuser защищена от удаления.'
            )

    @permission_required('superuser')
    async def create_role(
        self, request_obj: RoleDto, current_user: User
    ) -> Role:
        """Создание объекта роли."""
        await self._check_role_name(name=request_obj.name)
        return await self.db.create(request_obj)

    @permission_required('superuser')
    async def update_role(
        self, request_obj: RoleDto, role_id: UUID, current_user: User
    ) -> Role:
        """Обновление объекта роли."""
        role_obj = await self.get_obj_or_404(role_id)
        return await self.db.update(role_obj, request_obj)

    @permission_required('superuser')
    async def delete_role(self, role_id: UUID, current_user: User) -> None:
        """Удаление объекта роли."""
        role_obj = await self.get_obj_or_404(role_id)
        await self._check_protected_role(role_obj)
        return await self.db.delete(role_obj)

    @permission_required('superuser')
    async def get_roles_list(self, current_user: User) -> list[Role]:
        """Получение списка существующих ролей."""
        return await self.db.get_all()


@lru_cache()
def get_role_service(db: AsyncSession = Depends(get_session)) -> RoleService:
    return RoleService(db, Role)


class UserRoleService:
    """Сервис роли пользователя."""

    def __init__(self, db: AsyncSession):
        self.db = db

    """async def has_permission(
        self, user_id: UUID, permission_name: str
    ) -> bool:
        result = await self.db.execute(
            select(User)
            .join(UserRole)
            .join(Role)
            .where(
                User.id == user_id,
                Role.name == permission_name
            )
        )
        return bool(result.scalar_one_or_none())"""

    async def _get_user(self, user_id: UUID) -> User:
        """Получает пользователя по id."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден'
            )
        return user

    async def _get_role(self, role_id: UUID) -> Role:
        """Получает роль по id."""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Роль не найдена'
            )
        return role

    @permission_required('superuser')
    async def assign_role(self, role_operation: RoleOperation, current_user: User) -> UserRole:
        """Назначение роли"""
        user = await self._get_user(role_operation.user_id)
        role = await self._get_role(role_operation.role_id)
        existing_role = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == role_operation.user_id,
                UserRole.role_id == role_operation.role_id
            )
        )
        if existing_role.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Роль уже назначена пользователю'
            )
        user_role = UserRole(user_id=user.id, role_id=role.id)
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)
        return user_role

    @permission_required('superuser')
    async def remove_role(
        self, role_operation: RoleOperation, current_user: User
    ) -> None:
        """Удаление роли"""
        user_role = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == role_operation.user_id,
                UserRole.role_id == role_operation.role_id
            )
        )
        user_role = user_role.scalar_one_or_none()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Роль не назначена пользователю'
            )
        await self.db.delete(user_role)
        await self.db.commit()
