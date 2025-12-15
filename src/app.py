from fastapi import FastAPI

from .database.db import init_db, close_db, init_engine


async def lifespan(app: FastAPI):
    init_engine()
    await init_db()
    print("Database initialized")
    yield
    await close_db()


app = FastAPI(
    title="ToDo homework",
    description="Description of project",
    lifespan=lifespan
)


@app.get("/")
async def read_root():
    return {"message": "ToDo API is running"}

# uvicorn src.app:app --reload
# uvicorn app:app --reload --log-level debug
