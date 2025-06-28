import uuid
from http import HTTPStatus

import pytest_asyncio
import pytest
from tests.functional.src.constants import ASSIGN_URL, REGISTER_URL, REMOVE_URL, ROLE_URL

@pytest_asyncio.fixture
async def role_id(make_post_request_with_roles):
    resp = await make_post_request_with_roles(ROLE_URL, {'name': 'admin'})
    assert resp.status in (HTTPStatus.CREATED, HTTPStatus.CONFLICT)
    return (await resp.json())['id']

@ pytest.mark.asyncio
class TestRoleAssignment:
    """Тесты назначения ролей пользователям."""

    async def test_assign_role_to_user(self, make_post_request, make_post_request_with_roles, new_user_data, role_id):
        reg = await make_post_request(REGISTER_URL, new_user_data)
        assert reg.status == HTTPStatus.CREATED
        user_id = (await reg.json())['id']

        resp = await make_post_request_with_roles(ASSIGN_URL, {
            'user_id': user_id,
            'role_id': role_id
        })
        assert resp.status == HTTPStatus.OK

    async def test_assign_same_role_twice(self, make_post_request, make_post_request_with_roles, new_user_data, role_id):
        reg = await make_post_request(REGISTER_URL, new_user_data)
        assert reg.status == HTTPStatus.CREATED
        user_id = (await reg.json())['id']

        for _ in range(2):
            resp = await make_post_request_with_roles(ASSIGN_URL, {
                'user_id': user_id,
                'role_id': role_id
            })

        assert resp.status == HTTPStatus.CONFLICT

    async def test_assign_role_to_nonexistent_user(self, make_post_request_with_roles, role_id):
        fake_user_id = str(uuid.uuid4())
        resp = await make_post_request_with_roles(ASSIGN_URL, {
            'user_id': fake_user_id,
            'role_id': role_id
        })
        assert resp.status in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)

    async def test_assign_nonexistent_role(self, make_post_request, make_post_request_with_roles, new_user_data):
        reg = await make_post_request(REGISTER_URL, new_user_data)
        assert reg.status == HTTPStatus.CREATED
        user_id = (await reg.json())['id']
        fake_role_id = str(uuid.uuid4())

        resp = await make_post_request_with_roles(ASSIGN_URL, {
            'user_id': user_id,
            'role_id': fake_role_id
        })
        assert resp.status in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)

@ pytest.mark.asyncio
class TestRoleRemoval:
    """Тесты удаления ролей у пользователей."""

    async def test_remove_role_from_user(self, make_post_request, make_post_request_with_roles, new_user_data, role_id):
        reg = await make_post_request(REGISTER_URL, new_user_data)
        assert reg.status == HTTPStatus.CREATED
        user_id = (await reg.json())['id']

        assign = await make_post_request_with_roles(ASSIGN_URL, {
            'user_id': user_id,
            'role_id': role_id
        })
        assert assign.status == HTTPStatus.OK

        remove = await make_post_request_with_roles(REMOVE_URL, {
            'user_id': user_id,
            'role_id': role_id
        })
        assert remove.status == HTTPStatus.OK

    async def test_remove_unassigned_role(self, make_post_request, make_post_request_with_roles, new_user_data, role_id):
        reg = await make_post_request(REGISTER_URL, new_user_data)
        assert reg.status == HTTPStatus.CREATED
        user_id = (await reg.json())['id']

        remove_resp = await make_post_request_with_roles(REMOVE_URL, {
            'user_id': user_id,
            'role_id': role_id
        })
        assert remove_resp.status == HTTPStatus.NOT_FOUND
