from datetime import UTC, datetime, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    HTTPException,
    Response,
)
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dependencies import (
    active_user_required,
    authenticate_user,
    get_current_user,
    get_reset_token,
    get_user_by_email,
    get_user_by_id,
    pwd_context,
)
from apps.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from apps.auth.reset_token import (
    create_reset_password_link,
    create_reset_password_token,
)
from apps.auth.utils import set_refresh_token_cookie
from apps.schemas import (
    ChangePassword,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserResponse,
)
from database.db import get_db
from database.models import ResetPasswordToken, User
from email_service.background_tasks import (
    send_change_password_email,
    send_registration_email,
    send_reset_password_email,
)
from settings import BASE_DIR

auth_router = APIRouter()


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account. The password must match the repeat_password field. Email must be unique.",
    response_description="Created user information"
)
async def register(
        user: UserCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
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

    background_tasks.add_task(send_registration_email, user_db.email, user_db.name)

    return user_db


@auth_router.post(
    "/token",
    response_model=Token,
    summary="User login",
    description="Authenticate a user and receive an access token. The refresh token is automatically set as an HTTP-only cookie. Updates the user's last_login timestamp.",
    response_description="Access token and token type"
)
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


@auth_router.post(
    "/token/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token. The refresh token must be provided as an HTTP-only cookie. A new refresh token is issued and set as a cookie.",
    response_description="New access token and token type"
)
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


@auth_router.post(
    "/logout",
    summary="User logout",
    description="Log out the current user by invalidating the refresh token and clearing the refresh token cookie. Requires authentication.",
    response_description="Logout confirmation message"
)
async def logout(
        response: Response,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    current_user.refresh_token = None
    await db.commit()

    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}


@auth_router.post(
    "/change_password",
    summary="Change user password",
    description=(
        "Change the password for the currently authenticated user. "
        "The user must provide their current password and a new password. "
        "An email notification is sent after a successful password change. "
        "Requires authentication and an active user account."
    ),
    response_description="Password change confirmation message",
    dependencies=[Depends(active_user_required)],
    status_code=status.HTTP_200_OK,
)
async def change_password(
        password: ChangePassword,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    if not pwd_context.verify(password.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    current_user.hashed_password = pwd_context.hash(password.new_password)
    await db.commit()

    background_tasks.add_task(send_change_password_email, current_user.email, current_user.name)

    return {"message": "Password successfully changed."}


@auth_router.post(
    "/reset_password/request",
    summary="Request password reset",
    description=(
        "Request a password reset email for a user account. "
        "If the email address is associated with an existing account, "
        "a password reset link will be sent. "
        "The response is the same regardless of whether the account exists."
    ),
    response_description="Password reset request result message",
    status_code=status.HTTP_200_OK,
)
async def reset_password_request(
        payload: ResetPasswordRequest,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(payload.email, db)

    if user:
        token = await create_reset_password_token(user, db)
        link = create_reset_password_link(token)
        background_tasks.add_task(
            send_reset_password_email,
            payload.email,
            link,
        )

    return {
        "message": "If the account exists, you will receive an email."
    }


@auth_router.get(
    "/reset_password",
    summary="Get password reset form",
    description=(
        "Serve the HTML password reset form. "
        "The user accesses this endpoint via the password reset link "
        "received by email, which contains a reset token as a query parameter. "
        "In production, this endpoint should be replaced with a frontend URL."
    ),
    response_description="HTML password reset form",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_password_form():
    frontend_dir = BASE_DIR / "frontend"
    html_file = frontend_dir / "reset-password.html"
    
    if not html_file.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset form not found"
        )
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@auth_router.post(
    "/reset_password/confirm",
    summary="Confirm password reset",
    description=(
        "Confirm a password reset using a one-time reset token. "
        "The token must be valid, not expired, and unused. "
        "After a successful reset, the token is invalidated and "
        "an email notification is sent to the user."
    ),
    response_description="Password reset confirmation message",
    status_code=status.HTTP_200_OK,
)
async def reset_password_confirm(
        payload: ResetPasswordConfirm,
        background_tasks: BackgroundTasks,
        reset_token: ResetPasswordToken = Depends(get_reset_token),
        db: AsyncSession = Depends(get_db),
):
    user = reset_token.user
    user.hashed_password = pwd_context.hash(payload.new_password)

    reset_token.used_at = datetime.now(UTC)

    await db.commit()

    background_tasks.add_task(
        send_change_password_email,
        user.email,
        user.name,
    )

    return {"message": "Password has been successfully reset"}
