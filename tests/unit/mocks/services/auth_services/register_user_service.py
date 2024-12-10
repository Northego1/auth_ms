from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import AuthError, DatabaseError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto

async def register_user_mock(user_register_schema: MsRequestRegisterDto):
    if user_register_schema.username != 'test_user':
        raise DatabaseError(
            status_code=401,
            detail='Имя пользователя уже занято'
        )
    return UserSchema(
            id='e325db35-6ab9-4945-9a81-e2b5466938a6',
            username="test_user",
            hashed_password=b'test_pass',
            email='test@email.com',
            is_active=True
        )

MockRegisterUserService = cast(
    auth_services.RegiserUserServiceProtocol,
    Mock()
)
MockRegisterUserService.register_user = AsyncMock(
    side_effect=register_user_mock
)
