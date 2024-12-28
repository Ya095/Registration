from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import InvalidTokenError
from fastapi import status, Request
from core.models.db_helper import db_helper
from registration_app.api_v1.auth.crud import get_user_by_username
from registration_app.api_v1.auth.helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)
from registration_app.api_v1.auth_crypto import utils as auth_utils
from core.schemas.user import UserSchema


async def get_access_jwt_from_cookie(
    request: Request
) -> str | None:
    access_token = request.cookies.get(f"{ACCESS_TOKEN_TYPE}_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    return access_token


async def get_refresh_jwt_from_cookie(
    request: Request
) -> str | None:
    refresh_token = request.cookies.get(f"{REFRESH_TOKEN_TYPE}_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

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
) -> UserSchema:
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

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r}. Expected {token_type!r}",
    )


async def get_user_by_token_sub(
    payload: dict,
    session: AsyncSession
) -> UserSchema:
    username: str | None = payload.get("sub")

    user = await get_user_by_username(session, username)
    if user:
        return UserSchema.model_validate(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="user not found",
    )


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload_access),
    session: AsyncSession = Depends(db_helper.session_getter)
) -> UserSchema:

    validate_token_type(payload, ACCESS_TOKEN_TYPE)

    return await get_user_by_token_sub(payload, session)


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload_refresh),
    session: AsyncSession = Depends(db_helper.session_getter)
) -> UserSchema:
    validate_token_type(payload, REFRESH_TOKEN_TYPE)

    return await get_user_by_token_sub(payload, session)

