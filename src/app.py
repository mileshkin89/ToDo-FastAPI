from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from apps.admin.routes import admin_router
from apps.analytics.routes import analytics_router
from apps.auth.dependencies import get_current_user
from apps.auth.routes import auth_router
from apps.task.routes import task_router
from database.db import close_db
from database.models import User
from infrastructure.redis.client import cleanup_pool
from settings import (
    BASE_DIR,
    admin_prefix,
    analytics_prefix,
    api_version_prefix,
    auth_prefix,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown operations."""
    yield
    await cleanup_pool()
    await close_db()


app = FastAPI(
    title="ToDo API",
    description="""
    A comprehensive ToDo management API built with FastAPI.
    
    ## Features
    
    * **User Authentication**: Secure JWT-based authentication with refresh tokens
    * **Task Management**: Create, read, update, and delete tasks with filtering and pagination
    * **Admin Panel**: User management and analytics for administrators
    * **Analytics**: Real-time analytics and statistics for tasks and users
    * **Role-Based Access Control**: Support for regular users and superusers
    
    ## Authentication
    
    The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:
    1. Register a new user via `/api/v1/auth/register`
    2. Login via `/api/v1/auth/token` to receive an access token
    3. Include the token in the Authorization header: `Bearer <access_token>`
    
    Refresh tokens are automatically set as HTTP-only cookies for enhanced security.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend", html=False),
    name="static",
)

app.include_router(admin_router, prefix=f"{api_version_prefix}{admin_prefix}", tags=["admin"])
app.include_router(auth_router, prefix=f"{api_version_prefix}{auth_prefix}", tags=["auth"])
app.include_router(task_router, prefix=f"{api_version_prefix}", tags=["tasks"])
app.include_router(analytics_router, prefix=f"{api_version_prefix}{analytics_prefix}", tags=["analytics"])


@app.get(
    "/",
    tags=["root"],
    summary="Health check endpoint",
    description="Returns a simple message indicating that the API is running.",
    response_description="API status message"
)
async def read_root():
    """Health check endpoint to verify API availability."""
    return {"message": "ToDo API is running"}


@app.get(
    "/protected",
    tags=["protected"],
    summary="Protected route example",
    description="Example of a protected route that requires authentication. Returns information about the authenticated user.",
    response_description="Protected route response with user information"
)
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route demonstrating authentication requirement."""
    return {
        "message": "This is a protected route",
        "user_email": current_user.email,
        "user_id": current_user.id,
        "is_superuser": current_user.is_superuser,
    }
