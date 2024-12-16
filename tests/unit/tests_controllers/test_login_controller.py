import pickle
from unittest.mock import MagicMock
from dependency_injector import providers
from api.v1.controllers.login_user_controller import LoginUserControllerImpl, LoginUserControllerProtocol
from api.v1.controllers.login_user_controller import (
    container
)
from aio_pika import IncomingMessage
from tests.unit.mocks.services import auth_services
from tests.unit.mocks.services import jwt_services
import pytest
from tests.unit.config_data import mock_user


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_body, exception",
    [
        (
            {
                "username": mock_user.username,
                "hashed_password": mock_user.hashed_password,
                "fingerprint": b"mozilla"
            },
            False
        ),
        (
            {
                "username": mock_user.username,
                "hashed_password": b"non_correct",
                "fingerprint": b"mozilla"
            },
            True
        ),
        (
            {
                "username": 123,
                "hashed_password": mock_user.hashed_password,
                "fingerprint": b"mozilla"
            },
            True
        )
    ]
)
async def test_login_controller(
        message_body: dict,
        exception: bool,
):
    '''
    Юнит тест для логин контроллера, перезаписываем зависимости на моки, 
    ожидаем схему со статус кодом 200 в удачном случае, а в случае ошибки
    от 400 до 600
    '''
    mock_message = MagicMock(spec=IncomingMessage)
    mock_message.body = pickle.dumps(message_body)
    container.login_controller.override(
        providers.Factory(
            LoginUserControllerImpl,
            UserAuthService=auth_services.MockUserAuthService,
            RefreshJwtService=jwt_services.MockRefreshJwtService,
            AccessJwtService=jwt_services.MockAccessJwtService,
            UserSessionService=auth_services.MockUserSessionService
        )
    )
    login_controller: LoginUserControllerProtocol = container.login_controller()
    result = await login_controller.login_user(message=mock_message)
    if exception:
        assert result.status_code >= 400
    else:
        assert 200 <= result.status_code < 300