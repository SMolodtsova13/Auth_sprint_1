from typing import Any, Dict
import aiohttp
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from settings import TestSettings
from models.role import Role, UserRole
from services.base import BaseService,  SuperUserCreate
from models.user import User
from testdata.test_model import UserData


@pytest_asyncio.fixture(scope='session')
async def settings():
    """Фикстура для получения настроек тестового окружения."""
    return TestSettings()


@pytest_asyncio.fixture(scope='session')
async def session():
    """Фикстура для создания тестовой сессии."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def http_client():
    """Фикстура для создания HTTP-клиента."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
def make_post_request(http_client, settings: TestSettings):
    """Фикстура для выполнения POST-запросов."""
    async def _make_request(endpoint: dict,  data: dict):
        url = f'{settings.service_url}{endpoint}'
        async with http_client.post(url, json=data) as response:
            return response
    return _make_request


@pytest_asyncio.fixture
async def create_superuser(db_session: AsyncSession):
    """Фикстура для создания суперпользователя."""
    user_data = {
        'login': 'admin',
        'password': 'admin_password',
        'first_name': 'Admin',
        'last_name': 'User'
    }

    user_service = BaseService(db_session, User)
    role_service = BaseService(db_session, Role)

    # Создаем пользователя
    user_obj = SuperUserCreate(**user_data)
    db_user = await user_service.create(user_obj)

    # Создаем роль суперпользователя
    role_obj = await role_service.create({'name': 'superuser'})

    # Назначаем роль пользователю
    user_role = UserRole(user=db_user, role=role_obj)
    db_session.add(user_role)
    await db_session.commit()

    return db_user


@pytest_asyncio.fixture
async def role_service(session: AsyncSession):
    """Фикстура для сервиса работы с ролями."""
    return BaseService(session, Role)


@pytest_asyncio.fixture
def get_superuser_data() -> Dict[str, Any]:
    """Фикстура для получения данных суперпользователя."""
    return UserData(
        login='admin',
        password='admin_password',
        first_name='Admin',
        last_name='User'
    ).dict()


@pytest_asyncio.fixture
async def get_access_token(make_post_request, get_superuser_data) -> str:
    """Фикстура для получения access токена суперпользователя."""
    login_data = {
        'login': get_superuser_data['login'],
        'password': get_superuser_data['password']
    }
    response = await make_post_request('/api/v1/auth/login', login_data)
    return response.json()['access_token']
