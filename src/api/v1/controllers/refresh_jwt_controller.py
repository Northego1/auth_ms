from typing import Annotated, Protocol, Self

from aio_pika import IncomingMessage
from pydantic import ValidationError


from exceptions import InvalidRequestDataError, MicroServiceError
from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from pydantic_schemas.request_schemas.ms_request_schemas import MsRequestRefreshJwtDto
from pydantic_schemas.response_schemas.auth_service_responses import MsResponseRefreshJwtSchema

from dependency_injector import containers, providers
from api.v1.services import auth_services
from api.v1.services import jwt_services
from pydantic_schemas.response_schemas.base_response_schema import DefaultMicroServiceResponseSchema
from config import settings


class RefreshJwtControllerProtocol(Protocol):
    async def refresh_access_token(
            self: Self,
            message: IncomingMessage
    ) -> MsResponseRefreshJwtSchema:
        '''
        Обновляет токен доступа, в случае различия текущего фингерпринта
        от фингерпринта записанного для этого рефреш токена в базе данных,
        деактивирует рефреш токен, путем соотвестующей записи из базы данных
        и возвращает ошибку клиента 403
        '''



class RefreshJwtControllerImpl:
    def __init__(
            self: Self,
            CurrentUserService: auth_services.CurrentUserServiceProtocol,
            UserSessionService: auth_services.UserSessionServiceProtocol,
            AccessJwtService: jwt_services.AccessTokenServiceProtocol,
            RefreshJwtService: jwt_services.RefreshJwtServiceProtocol
    ) -> None:
        self.CurrentUserService = CurrentUserService
        self.UserSessionService = UserSessionService
        self.AccessTokenService = AccessJwtService
        self.RefreshTokenService = RefreshJwtService


    async def refresh_access_token(
            self: Self,
            message: IncomingMessage
    ) -> MsResponseRefreshJwtSchema:
        try:
            try:
                request_schema = MsRequestRefreshJwtDto.from_message(message)
            except ValidationError as e:
                raise InvalidRequestDataError() from e        
            refresh_jwt_schema: RefreshTokenSchema = (
                self.RefreshTokenService.decode_and_validate_jwt(
                    token=request_schema.refresh_token,
                    token_type=settings.jwt.refresh_type
                )
            )
            user: UserSchema = await self.CurrentUserService.get_current_user(
                token_schema=refresh_jwt_schema
            )
            try:
                await (
                    self.UserSessionService.check_and_invalidate_session(
                        refresh_token_schema=refresh_jwt_schema,
                        current_fingerprint_hash=request_schema.fingerprint
                    )
                )
            except MicroServiceError as e:
                raise MicroServiceError(
                    status_code=403, 
                    detail='Подозрительные действия'
                ) from e
            access_token: AccessTokenSchema = self.AccessTokenService.create_token(
                user=user
            )
            response_schema = MsResponseRefreshJwtSchema(
                status_code=200,
                detail='success refreshed access token',
                access_token_info=access_token
            )
        except MicroServiceError as e:
            response_schema = DefaultMicroServiceResponseSchema(
                status_code=e.status_code,
                detail=e.detail,
            )

        return response_schema



class Container(containers.DeclarativeContainer):
    refresh_jwt_controller = providers.Factory(
        RefreshJwtControllerImpl,
        CurrentUserService=auth_services.CurrentUserService,
        UserSessionService=auth_services.UserSessionService,
        AccessJwtService=jwt_services.AccessJwtService,
        RefreshJwtService=jwt_services.RefreshJwtService,
    )

container = Container()
RefreshJwtController = container.refresh_jwt_controller

