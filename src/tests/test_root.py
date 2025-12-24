import pytest
from starlette import status


@pytest.mark.asyncio
async def test_healthcheck(client):
    """Test health check endpoint without database dependencies."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ToDo API is running"}


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client):
    """Ensure protected route rejects unauthenticated requests."""
    response = await client.get("/protected")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_protected_route_returns_current_user(client, test_user, valid_access_token):
    """Ensure protected route returns current authenticated user data."""
    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["message"] == "This is a protected route"
    assert data["user_id"] == test_user.id
    assert data["user_email"] == test_user.email
