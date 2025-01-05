from pydantic import BaseModel
from fastapi import APIRouter, Response, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserAuth, SuccessOperationUser, UserSchema
from .validation import authenticate_user
from .helpers import (
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from .utils_token_info import (
    get_current_auth_user_for_refresh,
    get_current_active_auth_user,
)
from registration_app.core.config import settings
from registration_app.core import SessionDep
from registration_app.exceptions import IncorrectUsernameOrPasswordException
from registration_app.core import UserModel

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["JWT"],
)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


@router.post("/login/", response_model=TokenInfo)
async def auth_user(
    response: Response,
    user_data: UserAuth = Form(),
    session: AsyncSession = SessionDep,
):
    print(user_data)
    user = await authenticate_user(session=session, user_data=user_data)
    if user is None:
        raise IncorrectUsernameOrPasswordException

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response.set_cookie(
        key=f"{ACCESS_TOKEN_TYPE}_token",
        value=access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key=f"{REFRESH_TOKEN_TYPE}_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_expire_minutes * 3600 * 24,
    )

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    response_model=SuccessOperationUser,
    response_model_exclude_none=True,
)
def logout_user(
    response: Response,
):
    response.delete_cookie(
        key=f"{REFRESH_TOKEN_TYPE}_token",
        httponly=True,
    )
    response.delete_cookie(
        key=f"{ACCESS_TOKEN_TYPE}_token",
        httponly=True,
    )

    return SuccessOperationUser(msg="You have successfully logged out.")


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
    response: Response,
    user: UserModel = Depends(get_current_auth_user_for_refresh),
):
    user_schema = UserSchema.model_validate(user)
    access_token = create_access_token(user_schema)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_expire_minutes * 60,
    )
    return TokenInfo(access_token=access_token)


@router.get("/users/me", response_model=UserSchema)
async def auth_user_check_self_info(
    user: UserModel = Depends(get_current_active_auth_user),
):
    return UserSchema.model_validate(user)