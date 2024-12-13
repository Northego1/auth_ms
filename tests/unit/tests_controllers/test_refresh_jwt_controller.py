import pickle
from unittest.mock import MagicMock
from dependency_injector import providers
from api.v1.controllers.refresh_jwt_controller import (
    RefreshJwtControllerImpl
)
from api.v1.controllers.refresh_jwt_controller import (
    container
)
from aio_pika import IncomingMessage
from tests.unit.mocks.services import auth_services
from tests.unit.mocks.services import jwt_services
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_body, exception",
    [
        (
            {
                "fingerprint": b"mozilla",
                "refresh_token": "refresh_token",
            },
            False
        ),
                (
            {
                "fingerprint": 123,
                "refresh_token": "refresh_token",
            },
            True
        ),
                (
            {
                "fingerprint": b"mozilla",
                "refresh_token": "non_correct",
            },
            True
        )
    ]
)
async def test_refresh_jwt_controller(
    message_body: dict,
    exception: bool
):
    mock_message = MagicMock(spec=IncomingMessage)
    mock_message.body = pickle.dumps(message_body)
    container.refresh_jwt_controller.override(
        providers.Factory(
            RefreshJwtControllerImpl,
            CurrentUserService=auth_services.MockCurrentUserService,
            UserSessionService=auth_services.MockUserSessionService,
            AccessJwtService=jwt_services.MockAccessJwtService,
            RefreshJwtService=jwt_services.MockRefreshJwtService,
        )
    )
    refresh_jwt_controller = container.refresh_jwt_controller()
    result = await refresh_jwt_controller.refresh_access_token(
        message=mock_message
    )
    if exception:
        assert result.status_code >= 400
    else:
        assert 200 <= result.status_code < 300