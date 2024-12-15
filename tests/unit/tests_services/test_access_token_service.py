from typing import Optional
import pytest

from exceptions import MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from api.v1.services.jwt_services.access_token_service import (
    container,
    AccessTokenServiceImpl
)
from dependency_injector import providers
from pydantic_schemas.jwt_schemas import AccessTokenSchema
from unit.mocks import repository
from unit.config_data import mock_user, mock_access_token



@pytest.mark.parametrize(
    "mock_user, expectation",
    [
        (
            mock_user,
            None
        ),
        (
            'non_correct',
            pytest.raises(MicroServiceError)
        )
    ]
)
def test_create_token(
    mock_user: UserSchema,
    expectation: Optional[pytest.raises]
):
    container.access_token_service.override(
        providers.Factory(
            AccessTokenServiceImpl,
            AccessTokenBlackListRepository=repository.MockAccessTokenBlackListRepository
        )
    )
    access_token_service = container.access_token_service()
    if expectation:
        with expectation:
            result = access_token_service.create_token(
                user=mock_user
            )
    else:
        result = access_token_service.create_token(
            user=mock_user
        )
        assert isinstance(result, AccessTokenSchema)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "access_token_schema, expectation",
    [
        (
            mock_access_token,
            None
        ),
        (
            'non_correct',
            pytest.raises(MicroServiceError)
        )
    ]
)
async def test_check_access_token_blacklist(
    access_token_schema: AccessTokenSchema,
    expectation: Optional[pytest.raises]
):
    container.access_token_service.override(
        providers.Factory(
            AccessTokenServiceImpl,
            AccessTokenBlackListRepository=repository.MockAccessTokenBlackListRepository
        )
    )
    access_token_service = container.access_token_service()
    if expectation:
        with expectation:
            result = await access_token_service.check_access_token_blacklist(
                access_token_schema=access_token_schema
            )
    else:
        result = await access_token_service.check_access_token_blacklist(
            access_token_schema=access_token_schema
        )
        assert result is None 