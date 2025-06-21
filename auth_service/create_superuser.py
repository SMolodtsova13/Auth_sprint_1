from getpass import getpass

import typer
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import async_session
from models.role import Role, UserRole
from models.user import User
from schemas.user import SuperUserCreate
from schemas.role import RoleCreate
from services.base import BaseService


app = typer.Typer()

# TODO после написания сервисов сделать рефакторинг


@app.command()
def create_superuser():
    asyncio.run(_create())


async def _check_user(db: AsyncSession, login):
    service = BaseService(db, User)
    return await service.get_by_kwargs(login=login)


async def _create_user(db: AsyncSession, login, password):
    service = BaseService(db, User)
    user_obj = SuperUserCreate(
        login=login,
        password=password,
        first_name='admin',
        last_name='admin'
    )
    return await service.create(user_obj)


async def _create_role(db: AsyncSession):
    service = BaseService(db, Role)
    obj = RoleCreate(name='superuser')
    return await service.create(obj)


async def _create_user_role(db: AsyncSession, user, role):
    obj = UserRole(user=user, role=role)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)


async def _create():
    async with async_session() as session:
        login = typer.prompt('Введите логин: ')
        if await _check_user(session, login):
            typer.echo(f'Пользователь с логином {login} уже существует.')
            raise typer.Exit(code=1)
        password = getpass('Введите пароль: ')
        confirm_password = getpass('Введите пароль еще раз: ')
        if password != confirm_password:
            typer.echo('Пароли не совпадают')
            raise typer.Exit(code=1)
        try:
            db_user_obj = await _create_user(session, login, password)
            db_role_obj = await _create_role(session)
            await _create_user_role(session, db_user_obj, db_role_obj)
            typer.echo('Суперпользователь успешно создан')
        except Exception as err:
            await session.rollback()
            typer.echo(f'Ошибка: {err}')
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
