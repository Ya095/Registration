from registration_app.core.config import settings
from registration_app.api_v1.auth.schemas import (
    CreateUser,
    SuccessOperation,
    UserName,
    UserChangePassword,
    DataId,
    UserPassword,
)
from fastapi import APIRouter, Form, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from .utils_token_info import (
    get_current_active_auth_user,
    get_current_token_payload_access,
)
from .helpers import REFRESH_TOKEN_TYPE, ACCESS_TOKEN_TYPE
from registration_app.core import TransactionSessionDep, UserModel
from registration_app.api_v1.dao import UsersDAO
from registration_app import exceptions
from registration_app.api_v1.auth_crypto.utils import validate_password

router = APIRouter(prefix=settings.api.v1.auth, tags=["Users DB"])


@router.post("/register", response_model=SuccessOperation)
async def basic_register(
    session: AsyncSession = TransactionSessionDep,
    user_data: CreateUser = Form(),
):
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters=UserName(username=user_data.username),
    )
    if user:
        raise exceptions.UserAlreadyExistsException

    await UsersDAO.add(
        session=session,
        values=user_data,
    )

    return SuccessOperation(
        msg="User created successfully!",
        username=user_data.username,
        email=user_data.email,
    )


@router.patch("/change_password", response_model=SuccessOperation)
async def change_password(
    passwords_data: UserChangePassword,
    user: UserModel = Depends(get_current_active_auth_user),
    session: AsyncSession = TransactionSessionDep,
):

    if not validate_password(
        passwords_data.current_password,
        user.password,
    ):
        raise exceptions.IncorrectCurrentPasswordException

    await UsersDAO.update(
        session=session,
        filters=DataId(id=user.id),
        values=UserPassword(password=passwords_data.current_password),
    )

    return SuccessOperation(
        msg="Password updated successfully!",
        username=user.username,
        email=user.email,
    )


@router.delete("/deactivate_user_account", response_model=SuccessOperation)
async def deactivate_account(
    response: Response,
    payload: dict = Depends(get_current_token_payload_access),
    session: AsyncSession = TransactionSessionDep,
):
    await UsersDAO.make_inactive_by_id(
        session=session,
        data_id=int(payload.get("sub")),
    )

    response.delete_cookie(
        key=f"{ACCESS_TOKEN_TYPE}_token",
        httponly=True,
        # secure=True,
    )
    response.delete_cookie(
        key=f"{REFRESH_TOKEN_TYPE}_token",
        httponly=True,
        # secure=True,
    )

    return SuccessOperation(
        msg=f"User deactivated successfully!",
        username=payload.get("username"),
        email=payload.get("email"),
    )
