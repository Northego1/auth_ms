from datetime import datetime, timedelta, timezone
from typing import Annotated, Protocol, Self
import uuid

from api.v1.repository.black_list_access_jwt_repository import (
    AccessJwtBlackListRepositoryProtocol,
    AccessTokenBlackListRepository
)
from api.v1.utils.jwt_utils import encode_jwt
from exceptions import MicroServiceError


from pydantic_schemas.from_orm.user_schema import UserSchema
from pydantic_schemas.jwt_schemas import AccessTokenPayloadSchema, AccessTokenSchema
from config import settings
from dependency_injector import providers, containers
from logger import message_logger as mes_log


class AccessTokenServiceProtocol(Protocol):
    def create_token(
            self: Self,
            user: UserSchema
    ) -> AccessTokenSchema:
        pass


    async def revoke_token(self: Self, access_token_schema: AccessTokenSchema):
        pass

    
    async def check_access_token_blacklist(
            self: Self,
            access_token_schema: AccessTokenSchema
    ):
        '''
        Метод проверяет находится ли токен доступа в черном списке
        если находится вызывает исключение
        '''


class AccessTokenServiceImpl:
    def __init__(
            self: Self,
            AccessTokenBlackListRepository: AccessJwtBlackListRepositoryProtocol
    ):
        self.AccessTokenBlackListRepository = AccessTokenBlackListRepository
        

    def create_token(
            self: Self,
            user: UserSchema
    ) -> AccessTokenSchema:
        try:
            payload = AccessTokenPayloadSchema(
                type=settings.jwt.access_type,
                sub=user.username,
                user_id=user.id,
                jti=uuid.uuid4(),
                email=user.email,
                exp=datetime.now(timezone.utc) + timedelta(
                    minutes=settings.jwt.access_expire
                )
            )
            mes_log.info('Encoding access token')
            encoded_token = encode_jwt(payload)
            access_token_schema = AccessTokenSchema(
                token=encoded_token,
                token_type=settings.jwt.access_type,
                payload=payload
            )
            return access_token_schema
        except Exception as e:
            mes_log.error(f'Uknown error creating access token: {e}')
            raise MicroServiceError(
                detail='Неизвестая ошибка создания токена доступа'
            )

    
    async def revoke_token(self: Self, access_token_schema: AccessTokenSchema):
        try:
            await self.AccessTokenBlackListRepository.add_access_token(
                jti=access_token_schema.payload.jti,
                expire_at=access_token_schema.payload.exp,
                access_token=access_token_schema.token
            )
        except MicroServiceError as e:
            raise MicroServiceError(detail="Ошибка работы с базой данных") from e


    async def check_access_token_blacklist(
            self: Self,
            access_token_schema: AccessTokenSchema
    ):
        if not await self.AccessTokenBlackListRepository.read_access_token(
            jti=access_token_schema.payload.jti
        ):
            raise MicroServiceError(status_code=403, detail='access_token_invalid')


class Container(containers.DeclarativeContainer):
    access_token_service = providers.Factory(
        AccessTokenServiceImpl,
        AccessTokenBlackListRepository=AccessTokenBlackListRepository
    )


container = Container()
AccessJwtService: AccessTokenServiceProtocol = container.access_token_service



