from typing import Optional
from unittest.mock import AsyncMock, patch
from dependency_injector import providers
from api.v1.services.auth_services.autorization_user_service import (
    UserAuthServiceImpl,
    container
)
from pydantic_schemas.from_orm.user_schema import UserSchema
from tests.unit.mocks import repository
from aio_pika import IncomingMessage
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto

import pytest

from tests.unit.mocks.services.auth_services.autorization_user_service import _verify_password_side_effect


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'user_login_schema, expectation',
    [
        (
            MsRequestLoginDto(
                username='test_user',
                hashed_password=b'test_pass',
                fingerprint=b'mozilla'
            ),
            None
        )
    ],
    ids=['correct_test']
)
async def test_user_auth_service(
    user_login_schema: MsRequestLoginDto,
    expectation: Optional[pytest.raises]
): 
    with patch.object(
        UserAuthServiceImpl,
        '_verify_password',
        new=AsyncMock(
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
        