from typing import Optional
from unittest.mock import Mock, patch
from dependency_injector import providers
from api.v1.services.auth_services.autorization_user_service import (
    UserAuthServiceImpl,
    container
)
from exceptions import AuthError
from pydantic_schemas.from_orm.user_schema import UserSchema
from tests.unit.mocks import repository
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto

import pytest

from tests.unit.mocks.services.auth_services.autorization_user_service import _verify_password_side_effect
from tests.unit.config_data import mock_user


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user_login_schema, expectation',
    [
        (
            MsRequestLoginDto(
                username=mock_user.username,
                hashed_password=mock_user.hashed_password,
                fingerprint=b'mozilla'
            ),
            None
        ),
        (
            MsRequestLoginDto(
                username=mock_user.username,
                hashed_password='non_correct',
                fingerprint=b'mozilla'
            ),
            pytest.raises(AuthError)
        ),
        (
            MsRequestLoginDto(
                username='non_correct',
                hashed_password=mock_user.hashed_password,
                fingerprint=b'mozilla'
            ),
            pytest.raises(AuthError)
        ),
    ]
)
async def test_user_auth_service(
    user_login_schema: MsRequestLoginDto,
    expectation: Optional[pytest.raises]
): 
    '''
    Юнит тест для сервиса аутентификации, перезаписываем зависимости на моки, 
    функция ожидает аксес токен схему, функция возвращает "UserSchema", 
    в случае ошибки ожидаем "expectation"
    '''
    with patch.object(
        UserAuthServiceImpl,
        '_verify_password',
        new=Mock(
            side_effect=_verify_password_side_effect
        )
    ):
        container.user_auth_service.override(
            providers.Factory(
                UserAuthServiceImpl,
                UserRepository=repository.MockUserRepository
            )
        )
        auth_service = container.user_auth_service()
        if expectation:
            with expectation:
                result = await auth_service.authentificate_user(
                    user_login_schema=user_login_schema
                )
        else:
            result = await auth_service.authentificate_user(
                user_login_schema=user_login_schema
            )
            assert isinstance(result, UserSchema)
        