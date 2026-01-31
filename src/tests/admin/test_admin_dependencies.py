import pytest
from fastapi import HTTPException

from apps.admin.dependencies import superuser_required
from database.models import User


@pytest.mark.asyncio
async def test_superuser_required_success(pwd_context):
    """Test that superuser_required allows access for superusers."""
    admin = User(
        email="admin@example.com",
        name="Admin",
        hashed_password=pwd_context.hash("admin"),
        is_active=True,
        is_superuser=True,
    )

    result = await superuser_required(current_user=admin)

    assert result is admin
    assert result.is_superuser is True


@pytest.mark.asyncio
async def test_superuser_required_forbidden(pwd_context):
    """Ensure superuser_required denies access for non-superusers."""
    user = User(
        email="user@example.com",
        name="User",
        hashed_password=pwd_context.hash("password"),
        is_active=True,
        is_superuser=False,
    )

    with pytest.raises(HTTPException) as exc:
        await superuser_required(current_user=user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "SuperUser privileges required"


