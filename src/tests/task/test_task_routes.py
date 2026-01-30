import pytest
from starlette import status

from app import api_version_prefix


@pytest.mark.asyncio
async def test_task_list_success(client, valid_access_token, test_task):
    """
    Ensure the authenticated user can retrieve their task list.
    """
    response = await client.get(
        f"{api_version_prefix}/tasks",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["id"] == test_task.id


@pytest.mark.asyncio
async def test_task_list_filter_completed(client, valid_access_token, test_task):
    """
    Ensure tasks can be filtered by completion status.
    """
    response = await client.get(
        f"{api_version_prefix}/tasks?completed=false",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["tasks"]) == 1


@pytest.mark.asyncio
async def test_create_task_success(client, valid_access_token):
    """
    Ensure a new task can be created by an authenticated user.
    """
    payload = {
        "title": "New Task",
        "description": "Task description",
    }

    response = await client.post(
        f"{api_version_prefix}/tasks",
        json=payload,
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]


@pytest.mark.asyncio
async def test_read_task_success(client, valid_access_token, test_task):
    """
    Ensure a user can retrieve their task by ID.
    """
    response = await client.get(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_task.id


@pytest.mark.asyncio
async def test_update_task_success(client, valid_access_token, test_task):
    """
    Ensure a task can be updated by its owner.
    """
    payload = {"title": "Updated title"}

    response = await client.put(
        f"{api_version_prefix}/tasks/{test_task.id}",
        json=payload,
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == payload["title"]


@pytest.mark.asyncio
async def test_toggle_task_success(client, valid_access_token, test_task):
    """
    Ensure task completion status can be toggled.
    """
    response = await client.patch(
        f"{api_version_prefix}/tasks/{test_task.id}/toggle",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["completed"] is True


@pytest.mark.asyncio
async def test_delete_task_success(client, valid_access_token, test_task):
    """
    Ensure a task can be deleted by its owner.
    """
    response = await client.delete(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_read_task_forbidden_for_other_user(
    client,
    another_access_token,
    test_task,
):
    response = await client.get(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {another_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_read_task_allowed_for_admin(
    client,
    admin_access_token,
    test_task,
):
    response = await client.get(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_task.id


@pytest.mark.asyncio
async def test_delete_task_forbidden_for_admin(
    client,
    admin_access_token,
    test_task,
):
    response = await client.delete(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_task_forbidden_for_other_user(
    client,
    another_access_token,
    test_task,
):
    response = await client.delete(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {another_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN