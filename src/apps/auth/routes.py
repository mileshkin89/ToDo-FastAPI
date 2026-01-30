from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dependencies import (
    authenticate_user,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
    pwd_context,
)
from apps.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from apps.auth.utils import set_refresh_token_cookie
from apps.schemas import Token, UserCreate, UserResponse
from database.db import get_db
from database.models import User

auth_router = APIRouter()


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    existing_user = await get_user_by_email(user.email, db)

    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")

    hashed_password = pwd_context.hash(user.password)
    user_db = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )

    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    return user_db


@auth_router.post("/token", response_model=Token)
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user_db = await authenticate_user(form_data.username, form_data.password, db)

    access_token = create_access_token(data={"sub": str(user_db.id)})
    refresh_token = create_refresh_token(data={"sub": str(user_db.id)})

    user_db.refresh_token = refresh_token
    user_db.last_login = datetime.now(timezone.utc)
    await db.commit()

    set_refresh_token_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.post("/token/refresh", response_model=Token)
async def refresh_token(
        response: Response,
        refresh_token: str = Cookie(None, alias="refresh_token"),
        db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_refresh_token(refresh_token)
    user_id: int = int(payload.get("sub"))

    user_db = await get_user_by_id(user_id, db)

    if user_db is None or user_db.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(data={"sub": str(user_db.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user_db.id)})

    user_db.refresh_token = new_refresh_token
    await db.commit()

    set_refresh_token_cookie(response, new_refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.post("/logout")
async def logout(
        response: Response,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    current_user.refresh_token = None
    await db.commit()

    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}
