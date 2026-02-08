from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.db import get_db
from database.models import ResetPasswordToken, User
from settings import api_version_prefix, auth_prefix, settings

from ..schemas import ResetPasswordConfirm
from .jwt import verify_access_token
from .reset_token import hash_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_version_prefix}{auth_prefix}/token")

pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_access_token(token)
    except HTTPException:
        raise

    user_id: int = int(payload.get("sub"))
    if user_id is None:
        raise credentials_exception

    user_db = await get_user_by_id(user_id, db)
    if user_db is None:
        raise credentials_exception

    return user_db


async def get_user_by_email(
        email: str,
        db: AsyncSession = Depends(get_db)
) -> User | None:
    """Get a user by email address."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


async def get_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db)
) -> User | None:
    """Get a user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


async def authenticate_user(
        email: str,
        password: str,
        db: AsyncSession = Depends(get_db)
):
    """Authenticate a user by email and password."""
    user_db = await get_user_by_email(email, db)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not pwd_context.verify(password, user_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_db


async def active_user_required(
        current_user: User = Depends(get_current_user),
) -> User:
    """Require active user for access."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Curren User Account is not active",
        )

    return current_user


async def get_reset_token(
        payload: ResetPasswordConfirm,
        db: AsyncSession = Depends(get_db),
) -> ResetPasswordToken:
    """Get a reset password token."""
    token_hash = hash_token(payload.token)

    stmt = (
        select(ResetPasswordToken)
        .options(selectinload(ResetPasswordToken.user))
        .where(
            ResetPasswordToken.token_hash == token_hash,
            ResetPasswordToken.used_at.is_(None),
            ResetPasswordToken.expires_at > datetime.now(UTC),
        )
    )

    result = await db.execute(stmt)
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    return reset_token