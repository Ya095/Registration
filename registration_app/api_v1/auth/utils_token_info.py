from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError
from registration_app.api_v1.auth.helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from registration_app import exceptions
from registration_app.api_v1.auth_crypto import utils as auth_utils
from registration_app.core import SessionDep, UserModel
from registration_app.api_v1.dao import UsersDAO
from .schemas import UserSchema, DataId


async def get_access_jwt_from_cookie(
    request: Request
) -> str | None:
    access_token = request.cookies.get(f"{ACCESS_TOKEN_TYPE}_token")
    if not access_token:
        raise exceptions.AccessTokenNotFound

    return access_token


async def get_refresh_jwt_from_cookie(
    request: Request
) -> str | None:
    refresh_token = request.cookies.get(f"{REFRESH_TOKEN_TYPE}_token")
    if not refresh_token:
        raise exceptions.RefreshTokenNotFound

    return refresh_token


async def get_current_token_payload_access(
    token: str = Depends(get_access_jwt_from_cookie)
) -> dict:
    try:
        payload = auth_utils.decode_jwt(token)
    except InvalidTokenError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {ex}",
        )

    return payload


async def get_current_token_payload_refresh(
    token: str = Depends(get_refresh_jwt_from_cookie)
) -> dict:
    try:
        payload = auth_utils.decode_jwt(token)
    except InvalidTokenError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {ex}",
        )

    return payload


def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True

    raise exceptions.InvalidTokenType


async def get_user_by_token_sub(
    payload: dict,
    session: AsyncSession
) -> UserModel:
    user_id = int(payload.get("sub"))

    user = await UsersDAO.find_one_or_none_by_id(
        data_id=user_id,
        session=session,
    )
    if user:
        return user

    raise exceptions.UserNotFound


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload_access),
    session: AsyncSession = SessionDep
) -> UserModel:

    validate_token_type(payload, ACCESS_TOKEN_TYPE)

    return await get_user_by_token_sub(payload, session)


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload_refresh),
    session: AsyncSession = SessionDep
) -> UserModel:
    validate_token_type(payload, REFRESH_TOKEN_TYPE)

    return await get_user_by_token_sub(payload, session)


async def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user)
) -> UserModel:
    if user.is_active:
        return user

    raise exceptions.InactiveUser


def superuser_required(
    user: UserModel = Depends(get_current_active_auth_user),
):
    if not user.is_superadmin:
        raise exceptions.ForbiddenException
