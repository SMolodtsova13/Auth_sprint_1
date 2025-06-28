import pytest
from http import HTTPStatus
from datetime import datetime

from tests.functional.src.constants import (
    REGISTER_URL,
    LOGIN_URL,
    USER_LOGIN_HISTORY_URL,
    USER_LOGOUT_URL,
)
from tests.functional.testdata.test_model import UserData

@pytest.mark.asyncio
async def test_get_user_login_history(make_post_request, new_user_data):
    await make_post_request(REGISTER_URL, new_user_data)
    # Логин
    login_resp = await make_post_request(
        LOGIN_URL,
        {'login': new_user_data['login'],
         'password': new_user_data['password']}
    )
    assert login_resp.status == HTTPStatus.OK
    tokens = await login_resp.json()
    access_token = tokens['access_token']

    # Делаем еще один логин для истории
    await make_post_request(
        LOGIN_URL,
        {'login': new_user_data['login'],
         'password': new_user_data['password']}
    )

    # Получение истории
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = await make_post_request(
        USER_LOGIN_HISTORY_URL, {}, headers=headers
    )
    assert resp.status == HTTPStatus.OK
    history = await resp.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    for entry in history:
        # Поле timestamp заменено на login_at
        assert 'login_at' in entry
        assert 'user_agent' in entry
        # login_at парсится корректно
        data = datetime.fromisoformat(entry['login_at'])
        assert isinstance(data, datetime)

@pytest.mark.asyncio
async def test_logout_user(
    make_post_request, new_user_data, get_superuser_token
):
    # Регистрация и логин пользователя
    await make_post_request(REGISTER_URL, new_user_data)
    login_resp = await make_post_request(
        LOGIN_URL,
        {'login': new_user_data['login'],
         'password': new_user_data['password']}
    )
    tokens = await login_resp.json()
    access_token = tokens['access_token']

    # Выход пользователя
    headers = {'Authorization': f'Bearer {access_token}'}
    response = await make_post_request(
        USER_LOGOUT_URL,
        {},
        headers=headers
    )
    assert response.status == HTTPStatus.OK

    # После логаута токен недействителен
    response2 = await make_post_request(
        USER_LOGIN_HISTORY_URL,
        {},
        headers=headers
    )
    assert response2.status == HTTPStatus.UNAUTHORIZED
