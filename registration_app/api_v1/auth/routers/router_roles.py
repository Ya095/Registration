from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core import (
    TransactionSessionDep,
    RoleModel,
    SessionDep,
    UserModel,
)
from registration_app.core.config import settings
from registration_app.api_v1.dao import RoleDAO, UsersDAO
from registration_app.core.utils.role_cache import RoleCache
from registration_app.api_v1.auth.schemas import (
    RoleSchema,
    SuccessOperation,
    ChangeRoleToUser,
    UserName,
)
from registration_app.api_v1.auth.utils_token_info import superuser_required
from registration_app.core.utils.enums import PortalRole
from registration_app.exceptions import ForbiddenException


router = APIRouter(prefix=settings.api.v1.role, tags=["Roles"])


@router.get(
    "/get_all_roles",
    response_model=list[RoleSchema],
    dependencies=[Depends(superuser_required)],
)
async def get_all_roles(
    session: AsyncSession = SessionDep,
):
    roles: list[RoleModel] = await RoleDAO.find_all(
        session,
        None,
    )
    return roles


@router.patch(
    "/change_user_role",
    response_model=SuccessOperation,
    response_model_exclude_none=True,
    dependencies=[Depends(superuser_required)],
)
async def change_user_role_by_username(
    username: str,
    role_name: PortalRole,
    session: AsyncSession = TransactionSessionDep,
):
    role_id = RoleCache.get_role_id(role_name)

    user_for_update: UserModel = await UsersDAO.find_one_or_none(
        session=session,
        filters=UserName(username=username),
    )

    if user_for_update.is_superadmin:
        raise ForbiddenException

    await UsersDAO.update(
        session,
        UserName(username=username),
        ChangeRoleToUser(role_id=role_id),
    )
    return SuccessOperation(
        msg=f"Role {role_name!r} assigned successfully to user {username!r}.",
    )
