import pickle
from unittest.mock import MagicMock
from dependency_injector import providers
from api.v1.controllers.register_user_controller import (
    RegisterUserControllerImpl
)
from api.v1.controllers.register_user_controller import (
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
                "username": "test_user",
                "hashed_password": b"test_pass",
                "email": "test@email.com"
            },
            False
        ),
        (
            {
                "username": "non_correct",
                "hashed_password": b"test_pass",
                "email": "test@email.com"
            },
            True
        ),
        (
            {
                "username": "test_user",
                "hashed_password": b"test_pass",
                "email": "already_exists@gmail.com"
            },
            True
        ),
        (
            {
                "username": "test_user",
                "hashed_password": b"test_pass",
                "email": "non_correct_email"
            },
            True
        )
    ],
    ids=[
        "correct_request, non_correct_username, email_alredy_exists, non_correct_email"
    ]
)
async def test_register_controller(
    message_body: dict,
    exception: bool
):
    mock_message = MagicMock(spec=IncomingMessage)
    mock_message.body = pickle.dumps(message_body)
    container.register_controller.override(
        providers.Factory(
            RegisterUserControllerImpl,
            RegisterUserService=auth_services.MockRegisterUserService
        )
    )
    register_controller = container.register_controller()
    result = await register_controller.register_user(
        message=mock_message
    )
    if exception:
        assert result.status_code >= 400
    else:
        assert 200 <= result.status_code < 300