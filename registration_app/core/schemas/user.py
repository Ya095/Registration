from pydantic import BaseModel, EmailStr, Field, ConfigDict
from decimal import Decimal


class CreateUser(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    email: EmailStr = Field(...)


class SuccessOperationUser(BaseModel):
    msg: str
    username: str | None = None
    email: EmailStr | None = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True, from_attributes=True)

    id: int
    username: str
    hashed_password: str
    email: EmailStr
    money: Decimal = Field(..., ge=0)
    is_active: bool = True
