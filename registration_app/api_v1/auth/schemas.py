from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    model_validator,
    computed_field,
)
from typing import Self
from decimal import Decimal
from registration_app.api_v1.auth_crypto.utils import hash_password
from registration_app.core.utils.role_cache import RoleCache
from registration_app.core.utils.enums import PortalRole


class UserName(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(
        min_length=3,
        max_length=30,
        description="Имя пользователя, от 3 до 30 символов",
    )


class DataId(BaseModel):
    id: int


class UserPassword(BaseModel):
    password: str = Field(
        min_length=8,
        description="Пароль, от 8 знаков",
    )

    @model_validator(mode="after")
    def check_password(self) -> Self:
        """хешируем пароль до сохранения в БД"""

        self.password = hash_password(self.password).decode()
        return self


class UserAuth(UserPassword, UserName):
    def check_password(self) -> Self:
        return self


class CreateUser(UserPassword, UserName):
    email: EmailStr = Field(...)

    @computed_field
    def role_id(self) -> int:
        return RoleCache.get_role_id(PortalRole.USER)


class SuccessOperation(BaseModel):
    msg: str
    username: str | None = None
    email: EmailStr | None = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(
        min_length=8,
        description="Пароль, от 8 знаков",
    )

    @model_validator(mode="after")
    def check_password(self) -> Self:
        """хешируем пароль до сохранения в БД"""

        self.new_password = hash_password(self.new_password).decode()
        return self


class RoleName(BaseModel):
    name: PortalRole


class RoleSchema(DataId, RoleName):
    model_config = ConfigDict(from_attributes=True)


class ChangeRoleToUser(BaseModel):
    role_id: int


class UserSchema(UserName, DataId):
    email: EmailStr
    is_active: bool
    money: Decimal = Field(decimal_places=2)
    role_id: int
