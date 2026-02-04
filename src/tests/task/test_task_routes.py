from datetime import datetime

import pytest
from starlette import status

from app import api_version_prefix
from database.models import Task


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
    """Ensure users cannot read tasks belonging to other users."""
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
    """Test that admin can read tasks belonging to any user."""
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
    """Ensure admin cannot delete tasks belonging to other users."""
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
    """Ensure users cannot delete tasks belonging to other users."""
    response = await client.delete(
        f"{api_version_prefix}/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {another_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_task_forbidden_for_inactive_user(
    client,
    inactive_access_token,
):
    """Ensure inactive users cannot create tasks."""
    payload = {
        "title": "New Task",
        "description": "Task description",
    }

    response = await client.post(
        f"{api_version_prefix}/tasks",
        json=payload,
        headers={"Authorization": f"Bearer {inactive_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_task_forbidden_for_inactive_user(
    client,
    inactive_access_token,
    db_session,
    inactive_user,
):
    """Ensure inactive users cannot update tasks."""
    task = Task(
        title="Inactive User Task",
        description="Task description",
        completed=False,
        user_id=inactive_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    payload = {"title": "Updated title"}

    response = await client.put(
        f"{api_version_prefix}/tasks/{task.id}",
        json=payload,
        headers={"Authorization": f"Bearer {inactive_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_toggle_task_forbidden_for_inactive_user(
    client,
    inactive_access_token,
    db_session,
    inactive_user,
):
    """Ensure inactive users cannot toggle task completion status."""
    task = Task(
        title="Inactive User Task",
        description="Task description",
        completed=False,
        user_id=inactive_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.patch(
        f"{api_version_prefix}/tasks/{task.id}/toggle",
        headers={"Authorization": f"Bearer {inactive_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_task_forbidden_for_inactive_user(
    client,
    inactive_access_token,
    db_session,
    inactive_user,
):
    """Ensure inactive users cannot delete tasks."""
    task = Task(
        title="Inactive User Task",
        description="Task description",
        completed=False,
        user_id=inactive_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    response = await client.delete(
        f"{api_version_prefix}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {inactive_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()