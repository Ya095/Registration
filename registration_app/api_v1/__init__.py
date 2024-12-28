from fastapi import APIRouter

from registration_app.core.config import settings
from .auth.views import router as basic_auth_router
from .auth.jwt_auth import router as jwt_auth_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(basic_auth_router)
router.include_router(jwt_auth_router)
