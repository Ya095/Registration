from registration_app.core.schemas.user import UserSchema
from registration_app.api_v1.auth_crypto import utils as auth_utils
from registration_app.core.config import settings
from datetime import timedelta


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)

    return auth_utils.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )


def create_access_token(user: UserSchema) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
    }

    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes
    )


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {
        "sub": str(user.id)
    }

    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    )
