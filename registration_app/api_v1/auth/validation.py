from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from registration_app.api_v1.auth_crypto.utils import validate_password
from registration_app.core import SessionDep
from registration_app.api_v1.dao import UsersDAO
from .schemas import UserName, UserAuth, UserSchema


async def authenticate_user(
    user_data: UserAuth,
    session: AsyncSession = SessionDep,
) -> Optional[UserSchema]:
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters=UserName(username=user_data.username),
    )

    if not user or not validate_password(
        password=user_data.password,
        hashed_password=user.password,
    ):
        return None

    return UserSchema.model_validate(user)
