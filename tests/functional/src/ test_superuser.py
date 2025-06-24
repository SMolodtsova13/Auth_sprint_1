import pytest
from http import HTTPStatus

from testdata.test_model import UserData


@pytest.mark.asyncio
async def test_create_superuser(make_post_request, get_superuser_data):
    """Тест создания суперпользователя."""
    data = get_superuser_data
    response = await make_post_request('/api/v1/auth/register', data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['login'] == data['login']
    assert 'password' not in response.json()


@pytest.mark.asyncio
async def test_superuser_login(make_post_request, get_superuser_data):
    """Тест входа суперпользователя."""
    data = {
        'login': get_superuser_data['login'],
        'password': get_superuser_data['password']
    }
    response = await make_post_request('/api/v1/auth/login', data)

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()


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
    ).dict()

    await make_post_request('/api/v1/auth/register', user_data)

    headers = {'Authorization': f'Bearer {get_access_token}'}
    role_data = {
        'user_id': user_data['id'],
        'role_name': 'admin'
    }

    response = await make_post_request(
        '/api/v1/roles/assign',
        role_data,
        headers=headers
    )

    assert response.status_code == HTTPStatus.OK
