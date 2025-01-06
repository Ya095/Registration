from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core import (
    TransactionSessionDep,
    RoleModel,
    UserModel,
    SessionDep,
    PortalRole,
)
from registration_app.core.config import settings
from registration_app.api_v1.dao import RoleDAO, UsersDAO
from registration_app.exceptions import ForbiddenException, InactiveUser
from .schemas import (
    RoleSchema,
    SuccessOperation,
    ChangeRoleToUser,
    UserName,
    RoleName,
)
from .utils_token_info import get_current_active_auth_user


router = APIRouter(prefix=settings.api.v1.role, tags=["Admins"])


@router.get("/get_all_roles", response_model=list[RoleSchema])
async def get_all_roles(
    session: AsyncSession = SessionDep,
):
    roles: list[RoleModel] = await RoleDAO.find_all(
        session,
        None,
    )
    return roles


@router.patch(
    "/add_role_to_user",
    response_model=SuccessOperation,
    response_model_exclude_none=True,
)
async def add_role_to_user_by_username(
    username: str,
    role_name: PortalRole,
    session: AsyncSession = TransactionSessionDep,
    user: UserModel = Depends(get_current_active_auth_user),
):
    if not user.is_superadmin:
        raise ForbiddenException

    role = await RoleDAO.find_one_or_none(
        session,
        RoleName(name=role_name),
    )

    await UsersDAO.update(
        session,
        UserName(username=username),
        ChangeRoleToUser(role_id=role.id),
    )
    return SuccessOperation(
        msg=f"Role assigned successfully to user {username!r}.",
    )
