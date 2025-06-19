from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.user import RoleOperation
from services.roles import RoleService
from services.auth import get_current_user
router = APIRouter(prefix='/roles', tags=['roles'])


@router.post(
    '/assign',
    status_code=HTTPStatus.OK
)
async def assign_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    role_service = RoleService(db)
    return await role_service.assign_role(role_operation, current_user.id)


@router.post(
    '/remove',
    status_code=HTTPStatus.OK
)
async def remove_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    role_service = RoleService(db)
    return await role_service.remove_role(role_operation, current_user.id)
