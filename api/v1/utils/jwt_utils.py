import jwt
from typing import Union

from config import settings
from exceptions import MicroServiceError
from pydantic_schemas.jwt_schemas import AccessTokenPayloadSchema, AccessTokenSchema, RefreshTokenPayloadSchema, RefreshTokenSchema, TokenTransportType


def encode_jwt(
        payload: Union[
            RefreshTokenPayloadSchema,
            AccessTokenPayloadSchema
        ],
        private_key: str = settings.jwt.private_key
) -> str:
        payload_copy = payload.model_copy()
        encoded_jwt = jwt.encode(
            payload=payload_copy.model_dump(),
            key=private_key,
            algorithm=settings.jwt.algorithm 
        )
        return encoded_jwt


def decode_and_verify_jwt(
        token: str | bytes,
        public_key: str = settings.jwt.public_key
) -> Union[AccessTokenSchema, RefreshTokenSchema]:
    try:
        payload: dict = jwt.decode(
            token,
            public_key, 
            algorithms=settings.jwt.algorithm
        )
    except jwt.PyJWTError:
        raise MicroServiceError(status_code=403, detail='Токен некорректен или просрочен')
    
    if payload['type'] == settings.jwt.refresh_type:
        return RefreshTokenSchema(
            token=token,
            payload=RefreshTokenPayloadSchema.model_validate(payload),
            token_type=settings.jwt.refresh_type,
            transport_type=TokenTransportType.COOKIE
        )
    else:
        return AccessTokenSchema(
            token=token,
            payload=AccessTokenPayloadSchema.model_validate(payload),
            token_type=settings.jwt.access_type,
            transport_type=TokenTransportType.BEARER
        )

    
