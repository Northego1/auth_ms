from typing import Protocol, Self

from aio_pika import IncomingMessage
from dependency_injector import containers, providers
from pydantic import ValidationError
from api.v1.services import jwt_services
from api.v1.utils.jwt_getters import decode_and_validate_jwt
from exceptions import InvalidRequestDataError, MicroServiceError
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLogoutDto
from pydantic_schemas.response_schemas.base_response_schema import DefaultMicroServiceResponseSchema
from config import settings
from logger import message_logger as mes_log


class LogoutUserControllerProtocol(Protocol):
    async def logout_user(
            self: Self,
            message: IncomingMessage
    ) -> DefaultMicroServiceResponseSchema:
        pass


class LogoutUserControllerImpl:
    def __init__(
            self: Self,
            AccessTokenService: jwt_services.AccessTokenServiceProtocol,
            RefreshTokenService: jwt_services.RefreshJwtServiceProtocol,
    ):
        self.AccessTokenService = AccessTokenService
        self.RefreshTokenService = RefreshTokenService



    async def logout_user(
            self: Self,
            message: IncomingMessage
    ) -> DefaultMicroServiceResponseSchema:
        try:
            try:
                request_schema = MsRequestLogoutDto.from_message(message)
            except ValidationError as e:
                raise InvalidRequestDataError() from e     
            access_token_schema = decode_and_validate_jwt(
                refresh_token=request_schema.access_token,
                token_type=settings.jwt.access_type
            )
            await self.AccessTokenService.revoke_token(
                access_token_schema=access_token_schema
            )
            if request_schema.refresh_token:
                refresh_jwt_schema = decode_and_validate_jwt(
                        refresh_token=request_schema.refresh_token,
                    token_type=settings.jwt.refresh_type
                )
                await self.RefreshTokenService.revoke_token(
                    'fingerprint_hash',
                    value=request_schema.refresh_token,
                    user_id=refresh_jwt_schema.payload.user_id
                )
            response_schema = DefaultMicroServiceResponseSchema(
                status_code=203,
                detail='success logout'
            )
        except MicroServiceError as e:
            response_schema = DefaultMicroServiceResponseSchema(
                status_code=e.status_code,
                detail=e.detail
            )
        mes_log.info(f'Response status {response_schema.status_code}')
        return response_schema



class Container(containers.DeclarativeContainer):
    logout_controller = providers.Factory(
        LogoutUserControllerImpl,
        AccessTokenService = jwt_services.AccessJwtService,
        RefreshTokenService = jwt_services.RefreshJwtService,

    )


container = Container()
LogoutController = container.logout_controller