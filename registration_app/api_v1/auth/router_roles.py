from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from registration_app.core import (
    TransactionSessionDep,
    RoleModel,
    SessionDep,
    PortalRole,
)
from registration_app.core.config import settings
from registration_app.api_v1.dao import RoleDAO, UsersDAO
from .schemas import (
    RoleSchema,
    SuccessOperation,
    ChangeRoleToUser,
    UserName,
    RoleName,
)
from .utils_token_info import superuser_required


router = APIRouter(prefix=settings.api.v1.role, tags=["Roles"])


@router.get("/get_all_roles", response_model=list[RoleSchema])
async def get_all_roles(
    session: AsyncSession = SessionDep,
    _ = Depends(superuser_required),
):
    roles: list[RoleModel] = await RoleDAO.find_all(
        session,
        None,
    )
    return roles


# ToDo RoleCache user
@router.patch(
    "/add_role_to_user",
    response_model=SuccessOperation,
    response_model_exclude_none=True,
)
async def add_role_to_user_by_username(
    username: str,
    role_name: PortalRole,
    session: AsyncSession = TransactionSessionDep,
    _ = Depends(superuser_required),
):
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
