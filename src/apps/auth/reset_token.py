import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.models import ResetPasswordToken, User
from settings import api_version_prefix, auth_prefix, settings


def create_reset_password_link(token: str) -> str:
    """
    Generate a password reset link pointing to the HTML reset form.

    The generated URL is included in the password reset email and allows
    the user to access the password reset page using a one-time token.

    URL format:
        {BASE_URL}/api/v1/auth/reset_password?token={token}

    Note:
        In a production environment, this URL should be replaced with a frontend application URL.
    """
    return f"{settings.BASE_URL}{api_version_prefix}{auth_prefix}/reset_password?token={token}"


def hash_token(token: str) -> str:
    """
    Hash a reset password token using SHA-256.
    """
    return hashlib.sha256(token.encode()).hexdigest()


async def create_reset_password_token(
        user: User,
        db: AsyncSession,
) -> str:
    """
    Create and persist a one-time password reset token for a user.

    This function generates a secure random token, hashes it, and stores the
    hashed value in the database with an expiration timestamp. Only one active
    reset token per user is allowed at a time.

    If an active, non-expired reset token already exists for the user,
    a conflict error is raised.

    Args:
        user: User for whom the password reset token is being created.
        db: Asynchronous database session.

    Returns:
        The raw password reset token, which should be sent to the user via email.

    Raises:
        HTTPException: If an active password reset token already exists
        for the given user.
    """
    existing_token = await db.scalar(
        select(ResetPasswordToken).where(
            ResetPasswordToken.user_id == user.id,
            ResetPasswordToken.used_at.is_(None),
            ResetPasswordToken.expires_at > datetime.now(UTC),
        )
    )

    if existing_token is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A reset password request is already active for this account.",
        )

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    expires_at = datetime.now(UTC) + timedelta(minutes=settings.RESET_TOKEN_TTL_MINUTES)

    reset_token = ResetPasswordToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expires_at,
    )

    db.add(reset_token)

    try:
        await db.commit()
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A reset password request is already active for this account.",
        ) from err

    return raw_token
