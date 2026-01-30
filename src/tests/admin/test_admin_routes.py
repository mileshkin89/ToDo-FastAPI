import pytest
from starlette import status

from app import admin_prefix, api_version_prefix, app
from apps.auth.dependencies import get_current_user


@pytest.mark.asyncio
async def test_admin_routes_forbidden(client, test_user):
    async def override_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_user

    response = await client.get(f"{api_version_prefix}{admin_prefix}/users")

    assert response.status_code == 403
    assert response.json()["detail"] == "SuperUser privileges required"

    app.dependency_overrides.clear()


# GET /admin/users

@pytest.mark.asyncio
async def test_get_users_success(client, override_admin):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "users" in data
    assert "pagination" in data
    assert isinstance(data["users"], list)


@pytest.mark.asyncio
async def test_get_users_filter_active(client, override_admin):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users?active=true")

    assert response.status_code == 200
    for user in response.json()["users"]:
        assert user["is_active"] is True


@pytest.mark.asyncio
async def test_get_users_invalid_sort(client, override_admin):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users?sort_by=invalid")

    assert response.status_code == 400
    assert "Cannot sort by" in response.json()["detail"]


# GET /admin/users/{user_id}

@pytest.mark.asyncio
async def test_get_user_success(
        client,
        override_admin,
        test_user,
):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_user_not_found(client, override_admin):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# PATCH /admin/users/{user_id}/deactivate

@pytest.mark.asyncio
async def test_deactivate_user(
        client,
        override_admin,
        test_user,
):
    response = await client.patch(f"{api_version_prefix}{admin_prefix}/users/{test_user.id}/deactivate")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


# PATCH /admin/users/{user_id}/activate

@pytest.mark.asyncio
async def test_activate_user(
        client,
        override_admin,
        test_user,
        db_session,
):
    test_user.is_active = False
    await db_session.commit()

    response = await client.patch(f"{api_version_prefix}{admin_prefix}/users/{test_user.id}/activate")

    assert response.status_code == 200
    assert response.json()["is_active"] is True


# GET /admin/users/{user_id}/tasks

@pytest.mark.asyncio
async def test_get_tasks_by_user(
        client,
        override_admin,
        test_user,
        test_task,
):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users/{test_user.id}/tasks")

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["id"] == test_user.id
    assert isinstance(data["tasks"], list)
    assert data["pagination"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_tasks_by_user_completed_filter(
        client,
        override_admin,
        test_user,
        test_task,
):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users/{test_user.id}/tasks?completed=false")

    assert response.status_code == 200
    for task in response.json()["tasks"]:
        assert task["completed"] is False


@pytest.mark.asyncio
async def test_get_tasks_by_user_user_not_found(
        client,
        override_admin,
):
    response = await client.get(f"{api_version_prefix}{admin_prefix}/users/99999/tasks")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
