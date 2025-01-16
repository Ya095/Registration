from fastapi import status, HTTPException


UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The user already exists.",
)

IncorrectUsernameOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password.",
)


IncorrectCurrentPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The current password is incorrect.",
)


TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The token has expired.",
)

AccessTokenNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access token was not provided.",
)

RefreshTokenNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Refresh token was not provided.",
)

NoJwtException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The token is not valid.",
)

NoUserIdException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The user's ID was not found.",
)

UserNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User not found.",
)

ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough rights.",
)

UnexpectedException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"An unexpected error occurred."
)

InactiveUser = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User inactive.",
)

InvalidTokenType = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token type.",
)