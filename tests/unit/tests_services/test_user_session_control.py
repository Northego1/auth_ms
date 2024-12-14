from typing import Optional, Union
from dependency_injector import providers
from api.v1.services.auth_services.user_session_control_service import (
    container,
    UserSessionServiceImpl
)
from exceptions import DatabaseError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from tests.unit.mocks import repository
import pytest
from tests.unit.config_data import mock_user, mock_refresh_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refresh_token_schema, fingerprint_hash, expectation",
    [
        (
            mock_refresh_token,
            b'mozilla',
            None
        ),
        (
            mock_refresh_token,
            'non_correct',
            pytest.raises(DatabaseError)
        ),
    ]
)
async def test_register_user_session(
    refresh_token_schema: RefreshTokenSchema,
    fingerprint_hash: bytes,
    expectation: Optional[pytest.raises]
):
    container.user_session_service.override(
        providers.Factory(
            UserSessionServiceImpl,
            UserSessionRepository=repository.MockUserSessionRepository
        )
    )
    user_session_service = container.user_session_service()
    if expectation:
        with expectation:
            result = await user_session_service.register_user_session(
                refresh_token_schema=refresh_token_schema,
                fingerprint_hash=fingerprint_hash
            )
    else:
        result = await user_session_service.register_user_session(
            refresh_token_schema=refresh_token_schema,
            fingerprint_hash=fingerprint_hash
        )
        assert result is None



@pytest.mark.asyncio
@pytest.mark.parametrize(
    'refresh_token_schema, fingerprint_hash, expectation',
    [
        (
            mock_refresh_token,
            b'mozilla',
            None
        ),
        (
            mock_refresh_token,
            b'hochu_doner',
            pytest.raises(MicroServiceError)
        ),
    ]
)
async def test_check_and_invalidate_session(
    refresh_token_schema: RefreshTokenSchema,
    fingerprint_hash: bytes,
    expectation: Optional[pytest.raises]
):
    container.user_session_service.override(
        providers.Factory(
            UserSessionServiceImpl,
            UserSessionRepository=repository.MockUserSessionRepository
        )
    )
    user_session_service = container.user_session_service()
    if expectation:
        with expectation:
            result = await user_session_service.check_and_invalidate_session(
                refresh_token_schema=refresh_token_schema,
                current_fingerprint_hash=fingerprint_hash
            )
    else:
        result = await user_session_service.check_and_invalidate_session(
            refresh_token_schema=refresh_token_schema,
            current_fingerprint_hash=fingerprint_hash
        )
        assert result is None
