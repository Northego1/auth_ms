import hashlib
from typing import Protocol, Self

from api.v1.repository.user_session_repository import (
    UserSessionRepositoryProtocol,
    UserSessionRepository
)
from config import settings
from exceptions import DatabaseError, MicroServiceError
from pydantic_schemas.jwt_schemas import RefreshTokenSchema
from dependency_injector import containers, providers
from logger import message_logger as mes_log


class UserSessionServiceProtocol(Protocol):
    async def check_and_invalidate_session(
            self: Self,
            current_fingerprint_hash: bytes, 
            refresh_token_schema: RefreshTokenSchema
    ):
        pass

    
    async def register_user_session(
            self: Self,
            fingerprint_hash: bytes,
            refresh_token_schema: RefreshTokenSchema
    ):
        '''
        записывает в бд refresh token и фингерпринт клиента,
        если такой уже есть, то обновляет refresh token,
        если нет, то создает новую запись,
        если записей больше чем указано в настройках,
        удаляет одну по самому старому рефреш токену и создает
        новую сессию
        '''


    async def _create_or_replace_session(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: bytes,
    ):
        pass


    async def _update_session_if_exist(
            self: Self,
            refresh_token_schema,
            fingerprint_hash
    ) -> bool:
        pass


    async def _create_session(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: bytes
    ):
        pass


class UserSessionServiceImpl:
    def __init__(
            self: Self,
            UserSessionRepository: UserSessionRepositoryProtocol,
    ):
        self.UserSessionRepository = UserSessionRepository


    async def register_user_session(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: bytes
    ):
        try:
            mes_log.info(
                'Trying to update user session if session with current '
                'fingerprint exists') 
            if not await self._update_session_if_exist(
                refresh_token_schema=refresh_token_schema,
                fingerprint_hash=fingerprint_hash
            ):
                mes_log.info('Trying to create new session')
                await self._create_or_replace_session(
                    refresh_token_schema=refresh_token_schema,
                    fingerprint_hash=fingerprint_hash
                )
        except DatabaseError as e:
            mes_log.error(f'Failed to register user session: {e}')
            raise DatabaseError(
                detail='Ошибка регистрации сессии пользователя, ошибка базы данных'
            )


    async def check_and_invalidate_session(
            self: Self,
            current_fingerprint_hash: str, 
            refresh_token_schema: RefreshTokenSchema
    ):
        
        if await self.UserSessionRepository.delete_session_if_fingerprint_invalid(
                user_id=refresh_token_schema.payload.user_id,
                refresh_token=refresh_token_schema.token,
                fingerprint_hash=current_fingerprint_hash
        ):
            raise MicroServiceError(detail='Подозрительные действия')


    async def _create_or_replace_session(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: str,
    ):   
        if await self.UserSessionRepository.count_user_sessions(
               user_id=refresh_token_schema.payload.user_id
        ) >= settings.jwt.max_user_sessions:
            mes_log.info('Session count > max_limit, trying to delete oldest')
            await self.UserSessionRepository.delete_user_session(
                user_id=refresh_token_schema.payload.user_id
            )
            mes_log.info("Creating new user session")
            await self._create_session(
                refresh_token_schema=refresh_token_schema,
                fingerprint_hash=fingerprint_hash,
            ) 
        else:
            mes_log.info("Creating new user session")
            await self._create_session(
                refresh_token_schema=refresh_token_schema,
                fingerprint_hash=fingerprint_hash,
            )              


    async def _create_session(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: bytes
    ):
        await self.UserSessionRepository.create_user_session(
            refresh_token=refresh_token_schema.token,
            fingerprint_hash=fingerprint_hash,
            expire_at=refresh_token_schema.payload.exp,
            user_id=refresh_token_schema.payload.user_id
        )


    async def _update_session_if_exist(
            self: Self,
            refresh_token_schema: RefreshTokenSchema,
            fingerprint_hash: bytes
    ) -> bool:
        if await self.UserSessionRepository.is_session_exist(
            user_id=refresh_token_schema.payload.user_id,
            fingerprint_hash=fingerprint_hash
        ):
            await self.UserSessionRepository.update_user_session(
                fingerprint_hash=fingerprint_hash,
                user_id=refresh_token_schema.payload.user_id,
                refresh_token=refresh_token_schema.token,
                expire_at=refresh_token_schema.payload.exp
            )
            return True
        return False


class Container(containers.DeclarativeContainer):
    user_session_service = providers.Factory(
        UserSessionServiceImpl,
        UserSessionRepository=UserSessionRepository
    )

container = Container()
UserSessionService = container.user_session_service
