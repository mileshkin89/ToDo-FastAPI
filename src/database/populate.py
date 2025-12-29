import asyncio
from random import randint, random

from faker import Faker
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.dependencies import pwd_context
from apps.auth.models import User
from apps.task.models import Task
from database.db import get_db_contextmanager, reset_db
from database.populate_data import get_random_task_data

fake = Faker()


async def _seed_users(
        count: int = 100,
        default_password: str = "pass123",
        db: AsyncSession | None = None
) -> None:
    if db is None:
        raise ValueError("AsyncSession is required")

    users_data = []

    for i in range(count):
        name = (fake.user_name() + str(i))[:30]
        email = name + "@example.com"
        hashed_password = pwd_context.hash(default_password)

        users_data.append({
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
            "refresh_token": None
        })
    try:
        await db.execute(insert(User), users_data)
        await db.commit()
        print(f"Successfully seeded {count} users")
    except Exception as exc:
        await db.rollback()
        raise RuntimeError(f"Error seeding users: {exc}") from exc


async def _seed_tasks(
        min_per_user: int = 0,
        max_per_user: int = 100,
        completion_probability: float = 0.7,
        db: AsyncSession | None = None
) -> None:
    if db is None:
        raise ValueError("AsyncSession is required")

    tasks_data = []

    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()

    if not users:
        print("There are no users in the database. Run `seed_users()` first.")
        return

    for user in users:
        num_tasks = randint(min_per_user, max_per_user)

        for _ in range(num_tasks):
            title, description = get_random_task_data()
            completed = random() < completion_probability

            tasks_data.append({
                "title": title,
                "description": description,
                "completed": completed,
                "user_id": user.id
            })

    if not tasks_data:
        print("There are no tasks data to insert.")
        return

    try:
        await db.execute(insert(Task), tasks_data)
        await db.commit()
        print(f"Successfully seeded {len(tasks_data)} tasks for {len(users)} users")
    except Exception as exc:
        await db.rollback()
        raise RuntimeError(f"Error seeding tasks: {exc}") from exc


async def main():
    await reset_db()

    print("Start seeding...")

    async with get_db_contextmanager() as db:
        await _seed_users(db=db)
        await _seed_tasks(db=db)

    print("Database successfully seeded.")


if __name__ == "__main__":
    asyncio.run(main())
