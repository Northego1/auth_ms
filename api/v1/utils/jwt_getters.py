from typing import Literal, Union
from api.v1.utils.jwt_utils import decode_and_verify_jwt
from exceptions import MicroServiceError
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema
from config import settings


def decode_and_validate_jwt(
        refresh_token: str,
        token_type: str
) -> RefreshTokenSchema | AccessTokenSchema:
    token: AccessTokenSchema | RefreshTokenSchema = decode_and_verify_jwt(refresh_token)
    if token.payload.type != token_type:
        raise MicroServiceError(status_code=403, detail="Неверный тип токена")
    return token


