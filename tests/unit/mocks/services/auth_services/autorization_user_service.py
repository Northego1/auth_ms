from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import AuthError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto


async def mock_authentificate_user(user_login_schema: MsRequestLoginDto):
    _verify_password_side_effect(user_login_schema.hashed_password)
    return_value=UserSchema(
        id='e325db35-6ab9-4945-9a81-e2b5466938a6',
        username="test_user",
        hashed_password=b'test_pass',
        email='test@email.com',
        is_active=True
    )
    return return_value


def _verify_password_side_effect(
        hashed_password_from_request: bytes,
):
    if hashed_password_from_request != b'test_pass':
        raise AuthError(detail='Неправильный пароль')


def _check_active_user_side_effect(user: UserSchema):
    if not user.is_active:
        raise AuthError(detail='Пользователь не активен')


MockUserAuthService = cast(
    auth_services.UserAuthServiceProtocol,
    Mock()
)
MockUserAuthService.authentificate_user = AsyncMock(
    side_effect=mock_authentificate_user
)
MockUserAuthService._verify_password = Mock(
    side_effect=_verify_password_side_effect,
)
MockUserAuthService._check_active_user = Mock(
    side_effect=_check_active_user_side_effect,
)
