from registration_app.api_v1.auth_crypto import utils as auth_utils
from registration_app.core.schemas.user import CreateUser
from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core.models.user import User
from sqlalchemy import select, insert, update, text
from sqlalchemy.exc import IntegrityError, OperationalError
from fastapi import HTTPException, status


exception_creating_user = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="An error occurred while creating the user",
)

exception_unexpected = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"An unexpected error occurred."
)


async def create_user(
    session: AsyncSession,
    user: CreateUser,
) -> None:
    password_hashed = auth_utils.hash_password(user.password).decode()

    try:
        stmt = (
            insert(User)
            .values(
                username=user.username,
                hashed_password=password_hashed,
                email=user.email
            )
        )
        await session.execute(stmt)
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    except OperationalError:
        # logger.error(f"Database error: {e}")
        await session.rollback()
        raise exception_creating_user

    except Exception as e:
        # logger.exception(f"Unexpected error creating user: {e}")
        await session.rollback()
        raise exception_unexpected


async def get_user_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:

    try:
        stmt = (
            select("*")
            .where(User.username == username)
        )
        res = await session.execute(stmt)
        return res.one_or_none()

    except OperationalError:
        # logger.exception(f"Unexpected error getting user: {e}")
        raise exception_unexpected
    except Exception as e:
        # logger.exception(f"Unexpected error getting user: {e}")
        print(e)
        raise exception_unexpected


async def update_user_password(
    session: AsyncSession,
    username: str,
    new_password: str
) -> None:
    password_hashed = auth_utils.hash_password(new_password).decode()

    try:
        stmt = (
            update(User)
            .where(User.username == username)
            .values(hashed_password=password_hashed)
        )

        await session.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
        await session.execute(stmt)
        await session.commit()

    except OperationalError:
        # logger.exception(f"Unexpected error getting user: {e}")
        await session.rollback()
        raise exception_unexpected
    except Exception as e:
        # logger.exception(f"Unexpected error getting user: {e}")
        await session.rollback()
        raise exception_unexpected


async def deactivate_user_account(
    session: AsyncSession,
    user_id: int,
) -> None:
    try:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )

        await session.execute(stmt)
        await session.commit()

    except OperationalError:
        # logger.exception(f"Unexpected error getting user: {e}")
        await session.rollback()
        raise exception_unexpected
    except Exception as e:
        # logger.exception(f"Unexpected error getting user: {e}")
        await session.rollback()
        raise exception_unexpected
