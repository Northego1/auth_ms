from typing import Optional, Union
from dependency_injector import providers
from api.v1.services.auth_services.register_user_service import (
    container,
    RegisterUserServiceImpl
)
from exceptions import MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from tests.unit.mocks import repository
import pytest
from tests.unit.config_data import mock_user


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_register_schema, expectation",
    [
        (
            MsRequestRegisterDto(
                username=mock_user.username,
                hashed_password=mock_user.hashed_password,
                email=mock_user.email
            ),
            None
        ),
        (
            'non_correct',
            pytest.raises(MicroServiceError)
        )
    ]
)
async def test_register_service(
    user_register_schema: MsRequestRegisterDto,
    expectation: Optional[pytest.raises]
):
    '''
    Юнит тест для сервиса регистрации пользователя, перезаписываем зависимости
    на моки, функция ожидает данные о запросе из gateway (Схему MsRequestRegisterDto),
    функция возвращает "UserSchema", в случае ошибки ожидаем "expectation"
    '''
    container.register_service.override(
        providers.Factory(
            RegisterUserServiceImpl,
            UserRepository=repository.MockUserRepository
        )
    )
    register_service = container.register_service()
    if expectation:
        with expectation:
            result = await register_service.register_user(
                user_register_schema=user_register_schema
            )
    else:
        result = await register_service.register_user(
            user_register_schema=user_register_schema
        )
        assert isinstance(result, UserSchema)