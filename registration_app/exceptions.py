from fastapi import status, HTTPException


UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже существует.",
)

IncorrectUsernameOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный логин или пароль.",
)


IncorrectCurrentPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Текущий пароль не верен.",
)


TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
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
    detail="Токен не валидный!",
)

NoUserIdException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не найден ID пользователя",
)

UserNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User not found.",
)

ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Недостаточно прав!",
)

UnexpectedException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"An unexpected error occurred."
)

InactiveUser = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User inactive!",
)

InvalidTokenType = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token type!",
)