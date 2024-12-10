from typing import Annotated, Protocol, Self, Union
from aio_pika import IncomingMessage
from dependency_injector import containers, providers

from api.v1.services import auth_services
from api.v1.services import jwt_services
from exceptions import InvalidRequestDataError, MicroServiceError

from logger import message_logger as mes_log


from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestLoginDto
from pydantic_schemas.response_schemas.auth_service_responses import MsResponseLoginSchema, MsLoginResponsePayload
from pydantic_schemas.response_schemas.base_response_schema import DefaultMicroServiceResponseSchema
from pydantic import ValidationError


class LoginUserControllerProtocol(Protocol):
    async def login_user(
            self: Self,
            message: IncomingMessage
    ) -> Union[MsResponseLoginSchema, DefaultMicroServiceResponseSchema]:
        '''
        Контроллер для аутентификации и авторизации пользователя.
        Сначала проходит аутентификацию. Затем если все ок, создаем рефреш
        токен, записываем сессию в бд, создаем токен доступа и возвращаем, 
        схему ответа.
        '''
        pass


class LoginUserControllerImpl:
    def __init__(
            self: Self,
            UserAuthService: auth_services.UserAuthServiceProtocol,
            RefreshJwtService: jwt_services.RefreshJwtServiceProtocol,
            AccessJwtService: jwt_services.AccessTokenServiceProtocol,
            UserSessionService: auth_services.UserSessionServiceProtocol,
    ):
        self.UserAuthService = UserAuthService
        self.RefreshJwtService = RefreshJwtService
        self.UserSessionService = UserSessionService
        self.AccessJwtService = AccessJwtService

    async def login_user(
            self: Self,
            message: IncomingMessage
    ) -> Union[MsResponseLoginSchema, DefaultMicroServiceResponseSchema]:
        try:
            try:
                request_schema= MsRequestLoginDto.from_message(message)
            except ValidationError as e:
                raise InvalidRequestDataError() from e
            mes_log.info(f"Authentificating user {request_schema.username!r}")
            user: UserSchema = await self.UserAuthService.authentificate_user(
                user_login_schema=request_schema
            )
            mes_log.info(f"User {request_schema.username!r} success authentificated")
            mes_log.info(f"Trying to create refresh token")
            refresh_token: RefreshTokenSchema = await self.RefreshJwtService.create_token(
                user=user
            )
            mes_log.info(f"Refresh token created")
            mes_log.info('Trying to register user session')
            await self.UserSessionService.register_user_session(
                fingerprint_hash=request_schema.fingerprint,
                refresh_token_schema=refresh_token
            )
            mes_log.info('User session registred')
            mes_log.info(f"Trying to create access token")
            access_token: AccessTokenSchema = self.AccessJwtService.create_token(
                user=user
            )
            mes_log.info('Access token created')
            mes_log.info('Forming response to "Gateway microservice"')
            response_payload_schema = MsLoginResponsePayload(
                access_token_info=access_token,
                refresh_token_info=refresh_token
            )
            response_schema = MsResponseLoginSchema(
                status_code=200,
                detail=f"success, welcome {user.username}",
                payload=response_payload_schema
            )
        except MicroServiceError as e:
            response_schema = DefaultMicroServiceResponseSchema(
                status_code=e.status_code,
                detail=e.detail,
            )

        return response_schema


class Container(containers.DeclarativeContainer):
    login_controller = providers.Factory(
        LoginUserControllerImpl,
        UserAuthService=auth_services.UserAuthService,
        RefreshJwtService=jwt_services.RefreshJwtService,
        AccessJwtService=jwt_services.AccessJwtService,
        UserSessionService=auth_services.UserSessionService
    )

container = Container()
LoginUserController = container.login_controller
