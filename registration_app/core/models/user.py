from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from sqlalchemy import (
    text,
    UniqueConstraint,
    Numeric,
)


class User(Base, IdIntPkMixin):
    """Модель пользователя"""

    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str]
    money: Mapped[Decimal] = mapped_column(Numeric, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"),
    )

    __table_args__ = (UniqueConstraint("username", "email"),)

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id = {self.id}, username = {self.username!r})"
        )

    def __repr__(self):
        return str(self)
