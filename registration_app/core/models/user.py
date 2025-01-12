from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from sqlalchemy import (
    text,
    UniqueConstraint,
    Numeric,
    TIMESTAMP,
    ForeignKey,
)
from registration_app.core.utils.enums import PortalRole


class User(Base, IdIntPkMixin):
    """Модель пользователя"""

    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    email: Mapped[str]
    money: Mapped[Decimal] = mapped_column(Numeric, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"),
    )

    __table_args__ = (UniqueConstraint("username", "email"),)

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"(id = {self.id}, "
            f"username = {self.username!r}, "
            f"email = {self.email!r})"
        )

    def __repr__(self):
        return str(self)

    @property
    def is_admin(self) -> bool:
        from registration_app.core.utils.role_cache import RoleCache
        return self.role_id == RoleCache.get_role_id(PortalRole.ADMIN)

    @property
    def is_superadmin(self) -> bool:
        from registration_app.core.utils.role_cache import RoleCache
        return self.role_id == RoleCache.get_role_id(PortalRole.SUPERADMIN)


class Role(Base, IdIntPkMixin):
    name: Mapped[PortalRole] = mapped_column(unique=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
