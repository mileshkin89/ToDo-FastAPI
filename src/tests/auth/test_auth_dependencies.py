import pytest
from fastapi import Depends, HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import app
from apps.auth.dependencies import (
    authenticate_user,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
)
from apps.auth.models import User


@pytest.mark.asyncio
async def test_get_user_by_email_found(
        db_session: AsyncSession,
        test_user: User,
):
    user = await get_user_by_email(test_user.email, db_session)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
        db_session: AsyncSession,
):
    user = await get_user_by_email("missing@example.com", db_session)

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_id_found(
        db_session: AsyncSession,
        test_user: User,
):
    user = await get_user_by_id(test_user.id, db_session)

    assert user is not None
    assert user.id == test_user.id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
        db_session: AsyncSession,
):
    user = await get_user_by_id(999999, db_session)

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_success(
        db_session: AsyncSession,
        test_user: User,
):
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
    response = await client.get("/test-current-user")

    assert response.status_code == 401
