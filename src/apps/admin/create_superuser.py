import asyncio
from getpass import getpass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from apps.auth.dependencies import pwd_context
from database import engine
from database.models import User


async def main():
    """Create a superuser interactively via command line."""
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with async_session() as session:
        exists = await session.execute(
            select(User).where(User.is_superuser.is_(True))
        )

        if exists.scalar_one_or_none():
            print(f"{'=' * 40}\nSuperuser already exists\n{'=' * 40}")
            return

    print("=== Create Superuser ===")

    email = input("Enter superadmin email: ").strip()
    if not email:
        print("=== Email cannot be empty ===")
        return

    password = getpass("Enter superadmin password: ")
    if not password:
        print("=== Password cannot be empty ===")
        return

    password_confirm = getpass("Confirm superadmin password: ")
    if password != password_confirm:
        print("=== Passwords do not match ===")
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        if result.scalar_one_or_none():
            print(f"=== User with email '{email}' already exists ===")
            return

        admin = User(
            email=email,
            hashed_password=pwd_context.hash(password),
            is_superuser=True,
            is_active=True,
        )

        session.add(admin)
        await session.commit()

        print(f"{'=' * 40}\nSuperuser successfully created\n{'=' * 40}")


if __name__ == "__main__":
    asyncio.run(main())

