from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from apps.admin.routes import admin_router
from apps.analytics.routes import analytics_router
from apps.auth.dependencies import get_current_user
from apps.auth.routes import auth_router
from apps.task.routes import task_router
from database.db import close_db
from database.models import User
from infrastructure.redis.client import cleanup_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await cleanup_pool()
    await close_db()


app = FastAPI(
    title="ToDo",
    description="Description of ToDo project",
    lifespan=lifespan
)

api_version_prefix = "/api/v1"
admin_prefix = "/admin"
auth_prefix = "/auth"
analytics_prefix = "/analytics"
app.include_router(admin_router, prefix=f"{api_version_prefix}{admin_prefix}", tags=["admin"])
app.include_router(auth_router, prefix=f"{api_version_prefix}{auth_prefix}", tags=["auth"])
app.include_router(task_router, prefix=f"{api_version_prefix}", tags=["tasks"])
app.include_router(analytics_router, prefix=f"{api_version_prefix}{analytics_prefix}", tags=["analytics"])


@app.get("/", tags=["root"])
async def read_root():
    return {"message": "ToDo API is running"}


@app.get("/protected", tags=["protected"])
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "This is a protected route",
        "user_email": current_user.email,
        "user_id": current_user.id
    }
