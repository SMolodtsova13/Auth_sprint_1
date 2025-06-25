from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.role import RoleOperation, RoleCreateDto, RoleDto
from services.roles import RoleService, UserRoleService, get_role_service

router = APIRouter(prefix='/roles', tags=['roles'])


@router.post(
    '/assign',
    summary='Добавление роли пользователю',
    status_code=status.HTTP_200_OK
)
async def assign_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
):
    """Добавление роли пользователю."""
    role_service = UserRoleService(db)
    return await role_service.assign_role(role_operation)


@router.post(
    '/remove',
    summary='Удаление роли пользователя',
    status_code=status.HTTP_200_OK
)
async def remove_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
) -> None:
    """Удаление роли пользователя."""
    role_service = UserRoleService(db)
    return await role_service.remove_role(role_operation)


@router.put(
    '/{role_id}',
    response_model=RoleDto,
    summary='Обновление роли',
    status_code=status.HTTP_200_OK
)
async def update_role(
    role_id: UUID,
    request_obj: RoleCreateDto,
    role_service: RoleService = Depends(get_role_service)
) -> RoleDto:
    """Обновление роли."""
    return await role_service.update_role(request_obj, role_id)


@router.delete(
    '/{role_id}',
    summary='Удаление роли',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service)
) -> None:
    """Удаление роли."""
    return await role_service.delete_role(role_id)


@router.get(
    '',
    response_model=list[RoleDto],
    summary='Вывод списка существующих ролей',
    status_code=status.HTTP_200_OK
)
async def get_roles_list(
    role_service: RoleService = Depends(get_role_service)
) -> list[RoleDto]:
    """Вывод списка существующих ролей."""
    return await role_service.get_roles_list()


@router.post(
    '',
    response_model=RoleDto,
    summary='Создание роли',
    status_code=status.HTTP_201_CREATED
)
async def create_role(
    request_obj: RoleCreateDto,
    role_service: RoleService = Depends(get_role_service)
) -> RoleDto:
    """Создание роли."""
    return await role_service.create_role(request_obj)
