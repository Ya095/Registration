from fastapi import APIRouter

from registration_app.core.config import settings
from .auth.router_users import router as basic_auth_router
from .auth.router_jwt_auth import router as jwt_auth_router
from .auth.router_admins import router as roles_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(basic_auth_router)
router.include_router(jwt_auth_router)
router.include_router(roles_router)
