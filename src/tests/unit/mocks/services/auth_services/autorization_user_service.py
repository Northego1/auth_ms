from typing import cast
from unittest.mock import AsyncMock, Mock

from api.v1.services import auth_services
from exceptions import AuthError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto
from tests.unit.config_data import mock_user


async def mock_authentificate_user(user_login_schema: MsRequestLoginDto):
    _verify_password_side_effect(
        username=user_login_schema.username,
        hashed_password_from_db=mock_user.hashed_password,
        hashed_password_from_request=user_login_schema.hashed_password
    )

    return mock_user


def _verify_password_side_effect(
        username: str,
        hashed_password_from_db: bytes,
        hashed_password_from_request: bytes,
):
    if hashed_password_from_request != hashed_password_from_db:
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
