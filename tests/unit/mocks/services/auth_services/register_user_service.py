from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import DatabaseError
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from tests.unit.config_data import mock_user


async def register_user_mock(user_register_schema: MsRequestRegisterDto):
    if user_register_schema.username != mock_user.username:
        raise DatabaseError(
            status_code=401,
            detail='Имя пользователя уже занято'
        )
    if user_register_schema.email != mock_user.email:
        raise DatabaseError(
            status_code=401,
            detail='Текущий адрес почты уже существует'
        )
    return mock_user


MockRegisterUserService = cast(
    auth_services.RegiserUserServiceProtocol,
    Mock()
)
MockRegisterUserService.register_user = AsyncMock(
    side_effect=register_user_mock
)
