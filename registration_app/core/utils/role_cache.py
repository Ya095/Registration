from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import TYPE_CHECKING
from registration_app.core.utils.enums import PortalRole
from registration_app.api_v1.dao import RoleDAO
from pydantic import BaseModel


if TYPE_CHECKING:
    from registration_app.core import RoleModel


class NameRole(BaseModel):
    name: str


class RoleCache:
    _roles_cache = {}

    @classmethod
    async def initialize_roles(cls, session: AsyncSession) -> None:
        """Инициализирует роли в базе данных, добавляя отсутствующие."""

        roles: list["RoleModel"] = await RoleDAO.find_all(session, None)

        existing_roles = {role.name for role in roles}
        required_roles = {role.value for role in PortalRole}  # type: ignore

        missing_roles = required_roles - existing_roles
        missing_roles_schemas: list[NameRole] = [NameRole(name=role_name) for role_name in missing_roles]

        if missing_roles:
            await RoleDAO.add_many(session, missing_roles_schemas)
            logger.info(f"Added missing roles: {missing_roles!r}")
        else:
            logger.info("All required roles are already present.")

    @classmethod
    async def load_roles(cls, session: AsyncSession) -> None:
        """Загружает роли из базы данных в кэш."""

        roles: list["RoleModel"] = await RoleDAO.find_all(session, None)
        cls._roles_cache = {role.name: role.id for role in roles}
        logger.info("Roles added to cache.")

    @classmethod
    def get_role_id(cls, role_name: PortalRole) -> int:
        """Получает ID роли из кэша."""

        role_id = cls._roles_cache.get(role_name)
        if role_id is None:
            logger.error("Role %r not found in the cache.", role_name)
            raise ValueError(f"Role '{role_name}' not found in the cache.")
        return role_id

    @classmethod
    def refresh_cache(cls, session: AsyncSession) -> None:
        """Обновляет кэш ролей."""

        cls.load_roles(session)
        logger.info("Cache for roles updated successfully.")
