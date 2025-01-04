from fastapi import status, HTTPException


UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже существует",
)

IncorrectUsernameOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный логин или пароль",
)

TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)

TokenNotFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
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
        detail="User not found n",
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