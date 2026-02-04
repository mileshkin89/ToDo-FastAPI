import pytest
from fastapi import Depends, HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import app
from apps.auth.dependencies import (
    active_user_required,
    authenticate_user,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
)
from database.models import User


@pytest.mark.asyncio
async def test_get_user_by_email_found(
        db_session: AsyncSession,
        test_user: User,
):
    """Test that get_user_by_email returns a user when found."""
    user = await get_user_by_email(test_user.email, db_session)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
        db_session: AsyncSession,
):
    """Test that get_user_by_email returns None when user is not found."""
    user = await get_user_by_email("missing@example.com", db_session)

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_id_found(
        db_session: AsyncSession,
        test_user: User,
):
    """Test that get_user_by_id returns a user when found."""
    user = await get_user_by_id(test_user.id, db_session)

    assert user is not None
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
        db_session: AsyncSession,
):
    """Test that get_user_by_id returns None when user is not found."""
    user = await get_user_by_id(999999, db_session)

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_success(
        db_session: AsyncSession,
        test_user: User,
):
    """Test that authenticate_user succeeds with correct credentials."""
    user = await authenticate_user(
        email=test_user.email,
        password="testpassword123",
        db=db_session,
    )

    assert user is not False
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(
        db_session: AsyncSession,
        test_user: User,
):
    """Ensure authenticate_user raises an error with incorrect password."""
    with pytest.raises(HTTPException) as exc:
        await authenticate_user(
            email=test_user.email,
            password="wrong-password",
            db=db_session,
        )

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect password"


@pytest.mark.asyncio
async def test_authenticate_user_user_not_found(
        db_session: AsyncSession,
):
    """Ensure authenticate_user raises an error for non-existent users."""
    with pytest.raises(HTTPException) as exc:
        await authenticate_user(
            email="unknown@example.com",
            password="any-password",
            db=db_session,
        )

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect username or password"


@app.get("/test-current-user")
async def _test_current_user_endpoint(
        current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }


@pytest.mark.asyncio
async def test_current_user_endpoint_success(client, valid_access_token, test_user):
    """Test that get_current_user returns the correct user from a valid token."""
    response = await client.get(
        "/test-current-user",
        headers={
            "Authorization": f"Bearer {valid_access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_success(
        db_session: AsyncSession,
        valid_access_token: str,
        test_user: User,
):
    """Test that get_current_user returns the correct user from a valid token."""
    user = await get_current_user(
        token=valid_access_token,
        db=db_session,
    )

    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.parametrize(
    "token, expected_detail",
    [
        ("invalid.token", "Invalid token"),
    ]
)
@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client, token, expected_detail):
    """Ensure get_current_user rejects invalid tokens."""
    response = await client.get(
        "/test-current-user",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == expected_detail


@pytest.mark.asyncio
async def test_get_current_user_no_token(
    client: AsyncClient,
):
    """Ensure get_current_user rejects requests without a token."""
    response = await client.get("/test-current-user")

    assert response.status_code == 401


@app.get("/test-active-user")
async def _test_active_user_endpoint(
    current_user: User = Depends(active_user_required),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }


@pytest.mark.asyncio
async def test_active_user_required_success(
    client,
    valid_access_token,
    test_user,
):
    """Test that active_user_required allows access for active users."""
    response = await client.get(
        "/test-active-user",
        headers={"Authorization": f"Bearer {valid_access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_active_user_required_forbidden_for_inactive_user(
    client,
    inactive_access_token,
    inactive_user,
):
    """Test that active_user_required rejects access for inactive users."""
    response = await client.get(
        "/test-active-user",
        headers={"Authorization": f"Bearer {inactive_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_active_user_required_direct_call_success(
    test_user: User,
):
    """Test that active_user_required returns active user when called directly."""
    # Pass current_user directly, bypassing Depends
    result = await active_user_required(current_user=test_user)

    assert result.id == test_user.id
    assert result.is_active is True


@pytest.mark.asyncio
async def test_active_user_required_direct_call_forbidden(
    inactive_user: User,
):
    """Test that active_user_required raises HTTPException for inactive users."""
    # Pass current_user directly, bypassing Depends
    with pytest.raises(HTTPException) as exc:
        await active_user_required(current_user=inactive_user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "not active" in exc.value.detail.lower()
