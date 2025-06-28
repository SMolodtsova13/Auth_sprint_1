import pytest
from http import HTTPStatus

from tests.functional.src.constants import (
    REGISTER_URL, LOGIN_URL,
    REFRESH_URL, CHANGE_CREDENTIALS_URL
)


@pytest.mark.asyncio
class TestRegistration:
    """Тесты регистрации пользователей."""

    async def test_user_registration(self, make_post_request, new_user_data):
        response = await make_post_request(REGISTER_URL, new_user_data)
        assert response.status == HTTPStatus.CREATED

        json_data = await response.json()
        assert 'id' in json_data
        assert json_data['first_name'] == new_user_data['first_name']
        assert json_data['last_name'] == new_user_data['last_name']

    async def test_registration_with_empty_password(
            self, make_post_request, new_user_data
        ):
        user_data = new_user_data.copy()
        user_data['password'] = ''
        response = await make_post_request(REGISTER_URL, user_data)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY  # 422

    async def test_registration_with_duplicate_login(
            self, make_post_request, new_user_data
        ):
        # Успешная регистрация
        await make_post_request(REGISTER_URL, new_user_data)

        # Попытка зарегистрировать с тем же логином
        response = await make_post_request(REGISTER_URL, new_user_data)
        assert response.status == HTTPStatus.CONFLICT  # 409


@pytest.mark.asyncio
class TestLogin:
    """Тесты аутентификации пользователя."""

    async def test_user_login(self, make_post_request, new_user_data):
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
        assert json_data.get('token_type') == 'bearer'

    async def test_login_with_wrong_password(
            self, make_post_request, new_user_data
        ):
        await make_post_request(REGISTER_URL, new_user_data)

        login_data = {
            'login': new_user_data['login'],
            'password': 'wrong_password',
        }
        response = await make_post_request(LOGIN_URL, login_data)
        assert response.status == HTTPStatus.UNAUTHORIZED  # 401


@pytest.mark.asyncio
class TestTokenRefresh:
    """Тесты обновления access-токена по refresh-токену."""

    async def test_token_refresh(self, make_post_request, new_user_data):
        await make_post_request(REGISTER_URL, new_user_data)

        login_data = {
            'login': new_user_data['login'],
            'password': new_user_data['password'],
        }
        login_response = await make_post_request(LOGIN_URL, login_data)
        tokens = await login_response.json()

        refresh_token = tokens['refresh_token']
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = await make_post_request(
            REFRESH_URL, {}, headers=headers
        )
        assert response.status == HTTPStatus.OK

    async def test_refresh_with_invalid_token(self, make_post_request):
        response = await make_post_request(
            REFRESH_URL,
            {},
            headers={'Authorization': 'Bearer invalidtoken'}
        )
        assert response.status == HTTPStatus.UNAUTHORIZED  # 401


@pytest.mark.asyncio
class TestChangeCredentials:
    """Тесты изменения логина и пароля пользователя."""

    async def test_change_login_and_password(self, make_post_request, new_user_data):
        # Регистрация и логин
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
            'new_password': 'new_secure_pass',
            'current_password': new_user_data['password']
        }

        response = await make_post_request(
            CHANGE_CREDENTIALS_URL, new_credentials, headers=headers
        )

        assert response.status == HTTPStatus.OK
        json_resp = await response.json()
        assert json_resp['message'] == 'Данные успешно изменены'

    async def test_change_credentials_without_auth(self, make_post_request):
        new_credentials = {
            'new_login': 'newlogin',
            'new_password': 'newpassword123',
            'current_password': 'whatever'
        }
        response = await make_post_request(CHANGE_CREDENTIALS_URL, new_credentials)
        assert response.status == HTTPStatus.FORBIDDEN  # 403


    async def test_change_credentials_with_invalid_data(
            self, make_post_request, new_user_data
        ):
        await make_post_request(REGISTER_URL, new_user_data)

        login_data = {
            'login': new_user_data['login'],
            'password': new_user_data['password'],
        }
        login_response = await make_post_request(LOGIN_URL, login_data)
        tokens = await login_response.json()

        access_token = tokens['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}

        # Пустой логин
        new_credentials = {
            'new_login': '',
            'current_password': new_user_data['password']
        }
        response = await make_post_request(
            CHANGE_CREDENTIALS_URL,
            new_credentials,
            headers=headers
        )
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

        # Короткий пароль
        new_credentials = {
            'new_password': '123',
            'current_password': new_user_data['password']
        }
        response = await make_post_request(
            CHANGE_CREDENTIALS_URL,
            new_credentials,
            headers=headers
        )
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
