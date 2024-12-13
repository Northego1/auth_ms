from datetime import datetime, timedelta, timezone
from typing import Annotated, Protocol, Self, Union
import uuid

from api.v1.repository.user_session_repository import (
    UserSessionRepositoryProtocol,
    UserSessionRepository
)
from api.v1.utils.jwt_getters import CheckJwt
from api.v1.utils.jwt_utils import encode_jwt
from exceptions import MicroServiceError


from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import RefreshTokenPayloadSchema, RefreshTokenSchema
from config import settings
from dependency_injector import providers, containers
from logger import message_logger as mes_log
from timer import timer


class RefreshJwtServiceProtocol(Protocol):
    async def create_token(
            self: Self,
            user: UserSchema,
    ) -> RefreshTokenSchema:
        '''
        формирует и кодирует refresh token используя функцию encode
        возвращает pydantic schema
        '''

        
    async def revoke_token(
            self: Self,
            revoke_by: str,
            value: str,
            user_id: uuid.UUID,
    ):
        pass


    def decode_and_validate_jwt(
            token: str,
            token_type: str
    ) -> RefreshTokenSchema:
        pass


class RefreshJwtServiceImpl(CheckJwt):
    def __init__(
            self: Self,
            UserSessionRepository: UserSessionRepositoryProtocol
    ):
        self.UserSessionRepository = UserSessionRepository


    async def create_token(
            self: Self,
            user: UserSchema,
    ) -> RefreshTokenSchema:
        try:
            mes_log.info('Forming refresh token payload')
            payload = RefreshTokenPayloadSchema(
                type=settings.jwt.refresh_type,
                sub=user.username,
                user_id=user.id,
                jti=uuid.uuid4(),
                exp=datetime.now(timezone.utc) + timedelta(
                    minutes=settings.jwt.refresh_expire
                )
            )
            mes_log.info('Encoding refresh token')
            encoded_token = encode_jwt(payload)
            refresh_token_schema = RefreshTokenSchema(
                token=encoded_token,
                token_type=settings.jwt.access_type,
                payload=payload
            )
            return refresh_token_schema
        except Exception as e:
            mes_log.error(f'Failed to create refresh token: {e}')
            raise MicroServiceError(
                detail='Неизвестная ошибка создания рефреш токена'
            )


    async def revoke_token(
            self: Self,
            revoke_by: str,
            value: str,
            user_id: uuid.UUID,
    ):
        try:
            if not await self.UserSessionRepository.delete_user_session(
                user_id=user_id,
                delete_by=revoke_by,
                value=value
            ):
                raise MicroServiceError('Не найдена сессия')
        except MicroServiceError as e:
            raise MicroServiceError(detail="Ошибка работы с базой данных") from e


class Container(containers.DeclarativeContainer):
    refresh_jwt_service = providers.Factory(
        RefreshJwtServiceImpl,
        UserSessionRepository=UserSessionRepository
    )


container = Container()
RefreshJwtService: RefreshJwtServiceProtocol = container.refresh_jwt_service
