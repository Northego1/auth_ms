import pickle
from unittest.mock import MagicMock
from dependency_injector import providers
from api.v1.controllers.logout_user_controller import (
    LogoutUserControllerImpl
)
from api.v1.controllers.logout_user_controller import (
    container
)
from aio_pika import IncomingMessage
from tests.unit.mocks.services import jwt_services
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_body, exception",
    [
        (
            {
                "access_token": "access_token",
                "refresh_token": "refresh_token",
                "fingerprint": b'mozilla'
            },
            False
        ),
        (
            {
                "access_token": "non_correct",
                "refresh_token": "refresh_token",
                "fingerprint": b'mozilla'
            },
            True
        ),
        (
            {
                "access_token": "access_token",
                "refresh_token": "non_correct",
                "fingerprint": b'mozilla'
            },
            True
        ),
        (
            {
                "access_token": "access_token",
                "refresh_token": "non_correct",
                "fingerprint": 123
            },
            True
        ),
    ]
)
async def test_logout_controller(
    message_body: dict,
    exception: bool
):
    mock_message = MagicMock(spec=IncomingMessage)
    mock_message.body = pickle.dumps(message_body)
    container.logout_controller.override(
        providers.Factory(
            LogoutUserControllerImpl,
            AccessTokenService=jwt_services.MockAccessJwtService,
            RefreshTokenService=jwt_services.MockRefreshJwtService
        )
    )
    logout_controller = container.logout_controller()
    result = await logout_controller.logout_user(
        message=mock_message
    )
    if exception:
        assert result.status_code >= 400
    else:
        assert 200 <= result.status_code < 300