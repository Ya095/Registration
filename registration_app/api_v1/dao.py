from registration_app.core import BaseDAO
from registration_app.core import UserModel, RoleModel


class UsersDAO(BaseDAO):
    model = UserModel


class RoleDAO(BaseDAO):
    model = RoleModel
