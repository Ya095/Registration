from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core.config import settings
from registration_app.api_v1.auth.helpers import (
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from registration_app.api_v1.auth.validation import (
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload_access,
)
from registration_app.core.schemas.user import UserSchema, SuccessOperationUser
from registration_app.core import db_helper
from .crud import get_user_by_username
from registration_app.api_v1.auth_crypto import utils as auth_utils
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Form, HTTPException, status, Response


router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["JWT"],
)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> UserSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    user = await get_user_by_username(session, username)
    if user is None:
        raise unauthed_exc

    user_schem = UserSchema.model_validate(user)

    if not auth_utils.validate_password(password, user_schem.hashed_password):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )

    return user_schem


async def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user),
) -> UserSchema:
    if user.is_active:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )


@router.post(
    "/login",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_user_issue_jwt(
    response: Response,
    user: UserSchema = Depends(validate_auth_user),
):
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
    _=Depends(get_current_token_payload_access),
):
    response.delete_cookie(
        key=f"{REFRESH_TOKEN_TYPE}_token",
        httponly=True,
    )
    response.delete_cookie(
        key=f"{ACCESS_TOKEN_TYPE}_token",
        httponly=True,
    )

    return SuccessOperationUser(
        msg="You have successfully logged out."
    )


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def auth_refresh_jwt(
    response: Response,
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_expire_minutes * 60,
    )
    return TokenInfo(access_token=access_token)


@router.get("/users/me")
async def auth_user_check_self_info(
    user: UserSchema = Depends(get_current_active_auth_user),
):
    return {"username": user.username, "email": user.email}
