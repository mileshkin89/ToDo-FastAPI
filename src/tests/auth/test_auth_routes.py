import pytest
from starlette import status

from app import api_version_prefix, auth_prefix


@pytest.mark.asyncio
async def test_get_users(client, test_user):
    """Ensure the users endpoint returns a list of registered users."""
    response = await client.get(f"{api_version_prefix}/users")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "users" in data
    assert len(data["users"]) == 1
    assert data["users"][0]["email"] == test_user.email


@pytest.mark.asyncio
async def test_register_success(client):
    """Verify that a new user can be successfully registered."""
    payload = {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "strongpassword123",
        "repeat_password": "strongpassword123"
    }

    response = await client.post(f"{api_version_prefix}{auth_prefix}/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_register_existing_user(client, test_user):
    """Ensure registering an already existing user returns an error."""
    payload = {
        "email": test_user.email,
        "name": "Test User",
        "password": "testpassword123",
        "repeat_password": "testpassword123"
    }

    response = await client.post(f"{api_version_prefix}{auth_prefix}/register", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User already registered"


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Verify that valid credentials return an access token and set a refresh cookie."""
    response = await client.post(
        f"{api_version_prefix}{auth_prefix}/token",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    cookies = response.cookies
    assert "refresh_token" in cookies


@pytest.mark.asyncio
async def test_refresh_token_success(client, test_user):
    """Ensure a valid refresh token returns a new access token and refresh cookie."""
    login_response = await client.post(
        f"{api_version_prefix}{auth_prefix}/token",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    refresh_token = login_response.cookies.get("refresh_token")
    assert refresh_token is not None

    client.cookies.set("refresh_token", refresh_token)

    import asyncio
    await asyncio.sleep(1)

    response = await client.post(
        f"{api_version_prefix}{auth_prefix}/token/refresh",
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    assert response.cookies.get("refresh_token") != refresh_token


@pytest.mark.asyncio
async def test_refresh_token_missing_cookie(client):
    """Ensure an error is returned when the refresh token cookie is missing."""
    response = await client.post(f"{api_version_prefix}{auth_prefix}/token/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token not found in cookies"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    """Ensure an invalid refresh token is rejected."""
    client.cookies.set("refresh_token", "invalid.token.value")

    response = await client.post(
        f"{api_version_prefix}{auth_prefix}/token/refresh",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"


@pytest.mark.asyncio
async def test_logout_success(client, test_user, valid_access_token):
    """Verify that logout clears the refresh token and invalidates the session."""
    login_response = await client.post(
        f"{api_version_prefix}{auth_prefix}/token",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    refresh_token = login_response.cookies.get("refresh_token")
    client.cookies.set("refresh_token", refresh_token)

    response = await client.post(
        f"{api_version_prefix}{auth_prefix}/logout",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Successfully logged out"

    assert response.cookies.get("refresh_token") is None

