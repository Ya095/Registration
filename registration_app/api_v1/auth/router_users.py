from registration_app.core.config import settings
from registration_app.api_v1.auth.schemas import (
    CreateUser,
    SuccessOperationUser,
    UserName,
)
from fastapi import APIRouter, Form
from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core import TransactionSessionDep
from registration_app.api_v1.dao import UsersDAO
from registration_app.exceptions import UserAlreadyExistsException

router = APIRouter(prefix=settings.api.v1.auth, tags=["User DB"])


@router.post("/register", response_model=SuccessOperationUser)
async def basic_register(
    session: AsyncSession = TransactionSessionDep,
    user_data: CreateUser = Form(),
):
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters=UserName(username=user_data.username)
    )
    if user:
        raise UserAlreadyExistsException

    await UsersDAO.add(
        session=session,
        values=user_data,
    )

    return SuccessOperationUser(
        msg="User created successfully!",
        username=user_data.username,
        email=user_data.email,
    )




# @router.patch("/change_password", response_model=SuccessOperationUser)
# async def change_password(
#     passwords_data: UserChangePassword,
#     user: UserSchema = Depends(get_current_active_auth_user),
#     session: AsyncSession = Depends(db_helper.session_getter),
# ):
#
#     if not validate_password(
#         passwords_data.current_password,
#         user.hashed_password,
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Current password is incorrect.",
#         )
#
#     await update_user_password(
#         session,
#         user.id,
#         passwords_data.new_password,
#     )
#
#     return SuccessOperationUser(
#         msg="Password updated successfully!",
#         username=user.username,
#         email=user.email,
#     )
#
#
# @router.delete("/deactivate_user_account", response_model=SuccessOperationUser)
# async def delete_account(
#     user: UserSchema = Depends(get_current_active_auth_user),
#     session: AsyncSession = Depends(db_helper.session_getter),
# ):
#     await deactivate_user_account(session, user.id)
#
#     return SuccessOperationUser(
#         msg=f"User deleted successfully!",
#         username=user.username,
#         email=user.email,
#     )
