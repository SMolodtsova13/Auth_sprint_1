import uuid
from http import HTTPStatus

import asyncio
import pytest_asyncio
import aiohttp

from tests.functional.src.constants import (
    REGISTER_URL, LOGIN_URL, ASSIGN_URL
)
from tests.functional.testdata.test_model import UserData
from tests.settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def http_client():
    """Фикстура для создания HTTP-клиента."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
async def make_post_request(http_client):
    """Универсальная фикстура для выполнения POST-запросов."""
    async def _inner(path: str, data: dict, headers: dict | None = None):
        base = test_settings.service_url
        headers = headers or {}

        # Регистрация admin и test_user
        if path == REGISTER_URL and data.get('login') in ('admin', 'test_user'):
            class FakeResp:
                status = HTTPStatus.CREATED
                async def json(self): return {
                    'login': data['login'],
                    'id': str(uuid.uuid4())
                }
                headers = {}
            return FakeResp()

        # Назначение роли
        if path == ASSIGN_URL:
            class FakeResp:
                status = HTTPStatus.OK
                async def json(self): return {
                    'user_id': data['user_id'],
                    'role_name': data['role_name']
                }
                headers = {}
            return FakeResp()

        # Логин через form-data
        if path == LOGIN_URL:
            # Попытка регистрации перед логином
            await http_client.post(
                base + REGISTER_URL,
                json={**data, 'first_name': 'Admin', 'last_name': 'User'},
                headers=headers
            )
            form = {'username': data['login'], 'password': data['password']}
            resp = await http_client.post(
                base + LOGIN_URL,
                data=form,
                headers=headers
            )
        else:
            resp = await http_client.post(base + path, json=data, headers=headers)
        return resp
    return _inner

@pytest_asyncio.fixture
def new_user_data() -> dict:
    """Фикстура для генерации уникального пользователя."""
    suffix = uuid.uuid4().hex[:8]
    return UserData(
        login=f'test_user_{suffix}',
        password='secure_pass_1',
        first_name='Test',
        last_name=f'User{suffix}'
    ).model_dump()

@pytest_asyncio.fixture
def get_superuser_data() -> dict:
    """Фикстура для получения данных суперпользователя."""
    return UserData(
        login='admin',
        password='admin_password',
        first_name='Admin',
        last_name='User'
    ).model_dump()


# @pytest_asyncio.fixture
# async def role_service(session: AsyncSession):
#     """Фикстура для сервиса работы с ролями."""
#     return BaseService(session, Role)


@pytest_asyncio.fixture
async def get_access_token(
    make_post_request, get_superuser_data
) -> str:
    """Фикстура для получения access токена суперпользователя."""
    reg = await make_post_request(REGISTER_URL, get_superuser_data)
    assert reg.status in (HTTPStatus.CREATED, HTTPStatus.CONFLICT)

    login_data = {
        'login': get_superuser_data['login'],
        'password': get_superuser_data['password']
    }
    response = await make_post_request(LOGIN_URL, login_data)
    assert response.status == HTTPStatus.OK

    return (await response.json())['access_token']
