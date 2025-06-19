from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.user import RoleOperation
from services.roles import RoleService

router = APIRouter(prefix='/roles', tags=['roles'])


@router.post(
    '/assign',
    status_code=HTTPStatus.OK
)
async def assign_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
):
    role_service = RoleService(db)
    return await role_service.assign_role(role_operation)


@router.post(
    '/remove',
    status_code=HTTPStatus.OK
)
async def remove_role(
    role_operation: RoleOperation,
    db: AsyncSession = Depends(get_session),
):
    role_service = RoleService(db)
    return await role_service.remove_role(role_operation)
