from http import HTTPStatus

import pytest

from tests.functional.src.constants import ASSIGN_URL, LOGIN_URL, REGISTER_URL
from tests.functional.testdata.test_model import UserData


@pytest.mark.asyncio
async def test_create_superuser(make_post_request, get_superuser_data):
    """Тест создания суперпользователя."""
    data = get_superuser_data
    response = await make_post_request(REGISTER_URL, data)

    assert response.status == HTTPStatus.CREATED
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
    get_superuser_data,
    get_access_token
):
    """Тест назначения роли суперпользователем."""
    user_data = UserData(
        login='test_user',
        password='test_password',
        first_name='Test',
        last_name='User'
    ).model_dump()

    reg_resp = await make_post_request(REGISTER_URL, user_data)
    assert reg_resp.status == HTTPStatus.CREATED

    reg_json = await reg_resp.json()
    user_id = reg_json['id']

    headers = {'Authorization': f'Bearer {get_access_token}'}
    role_data = {
        'user_id': user_id,
        'role_name': 'admin'
    }

    response = await make_post_request(
        ASSIGN_URL,
        role_data,
        headers=headers
    )
    assert response.status == HTTPStatus.OK
