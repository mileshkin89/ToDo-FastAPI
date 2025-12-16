from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from apps.auth.routes import user_router, auth_router
from database.db import init_db, close_db, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    await init_db()
    print("Database initialized")
    yield
    await close_db()


app = FastAPI(
    title="ToDo",
    description="Description of ToDo project",
    lifespan=lifespan
)

api_version_prefix = "/api/v1"
app.include_router(user_router, prefix=f"{api_version_prefix}", tags=["users"])
app.include_router(auth_router, prefix=f"{api_version_prefix}/auth", tags=["auth"])


@app.get("/")
async def read_root():
    return {"message": "ToDo API is running"}


@app.get("/protected", tags=["protected"])
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "This is a protected route",
        "user_name": current_user.name,
        "user_id": current_user.id
    }
