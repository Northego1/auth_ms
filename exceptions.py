
from typing import Self


class MicroServiceError(Exception):
    def __init__(
            self: Self,
            detail: str = 'Неизвестая ошибка сервера',
            status_code: int = 500,
            *args
    ):
        self.status_code = status_code
        self.detail = detail
        super().__init__(*args)


class InvalidRequestDataError(MicroServiceError):
    def __init__(
            self: Self,
            status_code: int = 400,
            detail: str = 'В запрос микросервиса переданы некорректные данные',
            *args
    ):
        super().__init__(
            detail=detail,
            status_code=status_code,
            *args
        )


class AuthError(MicroServiceError):
    def __init__(
            self: Self,
            status_code: int = 401,
            detail: str = 'Ошибка аутентификации',
            *args
    ):
        super().__init__(
            detail=detail,
            status_code=status_code,
            *args
        )


class ConnectionError(MicroServiceError):
    pass


class DatabaseError(MicroServiceError):
    pass

