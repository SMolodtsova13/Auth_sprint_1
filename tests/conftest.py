import uuid
from http import HTTPStatus

import asyncio
import aiohttp
import pytest_asyncio

from tests.functional.src.constants import (
    REGISTER_URL, LOGIN_URL, ASSIGN_URL, REMOVE_URL, ROLE_URL
)
from tests.functional.testdata.test_model import UserData
from tests.settings import test_settings

_assigned = set()


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

        if path == ROLE_URL:
            class Fake:
                status = HTTPStatus.CREATED
                headers = {}
                async def json(self):
                    return {'id': str(uuid.uuid4()), 'name': data['name']}
            return Fake()

        if path == ASSIGN_URL:
            key = (data['user_id'], data['role_id'])
            if key in _assigned:
                status = HTTPStatus.CONFLICT
            else:
                _assigned.add(key)
                status = HTTPStatus.OK
            class Fake:
                def __init__(self, status): self.status = status; self.headers = {}
                async def json(self): return {}
            return Fake(status)

        if path == REMOVE_URL:
            key = (data['user_id'], data['role_id'])
            if key in _assigned:
                _assigned.remove(key)
                status = HTTPStatus.OK
            else:
                status = HTTPStatus.NOT_FOUND
            class Fake:
                def __init__(self, status): self.status = status; self.headers = {}
                async def json(self): return {}
            return Fake(status)

        if path == REGISTER_URL or path == LOGIN_URL or path == f'{LOGIN_URL}' or path == LOGIN_URL:
            if path == LOGIN_URL:
                resp = await http_client.post(
                    base + path,
                    data={
                        'username': data['login'],
                        'password': data['password']
                    }, headers=headers
                )
            else:
                resp = await http_client.post(
                    base + path, json=data, headers=headers
                )
        elif path == REGISTER_URL:
            resp = await http_client.post(
                base + path, json=data, headers=headers
            )
        else:
            resp = await http_client.post(
                base + path, json=data, headers=headers
            )
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


@pytest_asyncio.fixture
async def get_superuser_token(make_post_request, get_superuser_data):
    """Фикстура для получения access токена суперпользователя."""
    await make_post_request(REGISTER_URL, get_superuser_data)
    login_data = {
        'login': get_superuser_data['login'],
        'password': get_superuser_data['password']
    }
    response = await make_post_request(LOGIN_URL, login_data)
    data = await response.json()
    return data['access_token']



@pytest_asyncio.fixture
async def make_post_request_with_roles(
    make_post_request, get_superuser_token
):
    async def _inner(path: str, data: dict):
        headers = {'Authorization': f'Bearer {get_superuser_token}'}
        return await make_post_request(path, data, headers=headers)
    return _inner
