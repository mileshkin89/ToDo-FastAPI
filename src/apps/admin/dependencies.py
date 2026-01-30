from fastapi import Depends, HTTPException
from starlette import status

from apps.auth.dependencies import get_current_user
from database.models import User


def superuser_required(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SuperUser privileges required",
        )
    return current_user