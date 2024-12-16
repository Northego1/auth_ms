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
from tests.unit.config_data import mock_refresh_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_body, exception",
    [
        (
            {
                "fingerprint": b"mozilla",
                "refresh_token": mock_refresh_token.token,
            },
            False
        ),
        (
            {
                "fingerprint": 123,
                "refresh_token": mock_refresh_token.token,
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
    '''
    Юнит тест для рефреш аксес токен контроллера, перезаписываем зависимости на моки, 
    ожидаем схему со статус кодом 200 в удачном случае, а в случае ошибки
    от 400 до 600
    '''
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