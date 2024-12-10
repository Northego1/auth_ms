from typing import Annotated, Protocol, Self

from aio_pika import IncomingMessage
from pydantic import ValidationError

from api.v1.services.auth_services.register_user_service import (
    RegiserUserServiceProtocol,
    RegisterUserService
)
from dependency_injector import containers, providers

from exceptions import InvalidRequestDataError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRegisterDto
from pydantic_schemas.response_schemas.auth_service_responses import MsResponseLoginSchema, MsResponseRegisterSchema
from pydantic_schemas.response_schemas.base_response_schema import DefaultMicroServiceResponseSchema


class RegisterUserControllerProtocol(Protocol):
    async def register_user(
            self: Self,
            message: IncomingMessage
    ) -> MsResponseRegisterSchema:
        pass



class RegisterUserControllerImpl:
    def __init__(
            self: Self,
            RegisterUserService: RegiserUserServiceProtocol,
    ):
        self.RegisterUserService= RegisterUserService


    async def register_user(
            self: Self,
            message: IncomingMessage
    ) -> MsResponseRegisterSchema:
        try:
            try:
                user_register_dto= MsRequestRegisterDto.from_message(
                    message
                )
            except ValidationError as e:
                raise InvalidRequestDataError() from e
            user: UserSchema = await self.RegisterUserService.register_user(
                user_register_schema=user_register_dto
            )
            response_schema = MsResponseRegisterSchema(
                status_code=204,
                detail=f"user {user.username} success registred",
                username=user.username,
                email=user.email
            )
        except MicroServiceError as e:
            response_schema = DefaultMicroServiceResponseSchema(
                status_code=e.status_code,
                detail=e.detail,
            )
        print(response_schema.status_code)
        return response_schema   

class Container(containers.DeclarativeContainer):
    user_register_service = providers.Factory(
        RegisterUserControllerImpl,
        RegisterUserService=RegisterUserService
    )

container = Container()
RegiserUserController = container.user_register_service