import pytest
from http import HTTPStatus

from tests.functional.src.constants import (
    CHANGE_CREDENTIALS_URL, LOGIN_URL,
    REFRESH_URL, REGISTER_URL
)


@pytest.mark.asyncio
async def test_user_registration(make_post_request, new_user_data):
    response = await make_post_request(REGISTER_URL, new_user_data)
    assert response.status == HTTPStatus.CREATED
    json_data = await response.json()
    assert json_data['login'] == new_user_data['login']


@pytest.mark.asyncio
async def test_user_login(make_post_request, new_user_data):
    await make_post_request(REGISTER_URL, new_user_data)

    login_data = {
        'login': new_user_data['login'],
        'password': new_user_data['password'],
    }
    response = await make_post_request(LOGIN_URL, login_data)

    assert response.status == HTTPStatus.OK
    json_data = await response.json()
    assert 'access_token' in json_data
    assert 'refresh_token' in json_data


@pytest.mark.asyncio
async def test_token_refresh(make_post_request, new_user_data):
    await make_post_request(REGISTER_URL, new_user_data)

    login_data = {
        'login': new_user_data['login'],
        'password': new_user_data['password'],
    }
    login_response = await make_post_request(LOGIN_URL, login_data)
    tokens = await login_response.json()

    refresh_token = tokens['refresh_token']
    response = await make_post_request(
        REFRESH_URL,
        {'refresh_token': refresh_token}
    )
    assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_change_login_and_password(make_post_request, new_user_data):
    await make_post_request(REGISTER_URL, new_user_data)

    login_data = {
        'login': new_user_data['login'],
        'password': new_user_data['password'],
    }
    login_response = await make_post_request(LOGIN_URL, login_data)
    tokens = await login_response.json()

    access_token = tokens['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    new_credentials = {
        'new_login': f"{new_user_data['login']}_updated",
        'new_password': 'new_secure_pass'
    }

    response = await make_post_request(
        CHANGE_CREDENTIALS_URL, new_credentials, headers=headers
    )

    assert response.status == HTTPStatus.OK
    assert (await response.json())['message'] == 'Данные успешно изменены'
