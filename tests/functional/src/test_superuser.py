import uuid
import pytest
from http import HTTPStatus

from tests.functional.src.constants import (
    ASSIGN_URL, LOGIN_URL, REGISTER_URL, ROLE_URL
)
from tests.functional.testdata.test_model import UserData


@pytest.mark.asyncio
async def test_create_superuser(make_post_request, get_superuser_data):
    """Тест создания суперпользователя."""
    data = get_superuser_data
    response = await make_post_request(REGISTER_URL, data)

    assert response.status in (HTTPStatus.CREATED, HTTPStatus.CONFLICT)
    if response.status == HTTPStatus.CREATED:
        body = await response.json()
        assert body['login'] == data['login']
        assert 'password' not in body


@pytest.mark.asyncio
async def test_superuser_login(make_post_request, get_superuser_data):
    """Тест входа суперпользователя."""
    data = {
        'login': get_superuser_data['login'],
        'password': get_superuser_data['password']
    }
    response = await make_post_request(LOGIN_URL, data)

    assert response.status == HTTPStatus.OK
    body = await response.json()
    assert 'access_token' in body
    assert 'refresh_token' in body


@pytest.mark.asyncio
async def test_superuser_role_assignment(
    make_post_request,
    make_post_request_with_roles,
    get_superuser_token
):
    """Тест назначения роли суперпользователем."""
    # генерируем уникального пользователя
    suffix = uuid.uuid4().hex[:8]
    user_data = UserData(
        login=f'test_user_{suffix}',
        password='test_password',
        first_name='Test',
        last_name='User'
    ).model_dump()

    reg_resp = await make_post_request(REGISTER_URL, user_data)
    assert reg_resp.status == HTTPStatus.CREATED
    reg_json = await reg_resp.json()
    user_id = reg_json['id']

    headers = {'Authorization': f'Bearer {get_superuser_token}'}
    # создаем роль admin
    resp_role = await make_post_request_with_roles(ROLE_URL, {'name': 'admin'})
    assert resp_role.status in (HTTPStatus.CREATED, HTTPStatus.CONFLICT)
    role_id = (await resp_role.json())['id']

    # назначаем роль пользователю
    resp_assign = await make_post_request(
        ASSIGN_URL,
        {'user_id': user_id, 'role_id': role_id},
        headers=headers
    )
    assert resp_assign.status == HTTPStatus.OK
