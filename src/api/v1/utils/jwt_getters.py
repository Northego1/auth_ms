from typing import Self
from api.v1.utils.jwt_utils import decode_and_verify_jwt
from exceptions import MicroServiceError
from pydantic_schemas.jwt_schemas import AccessTokenSchema, RefreshTokenSchema

class CheckJwt:
    def decode_and_validate_jwt(
            self: Self,
            token: str,
            token_type: str
    ) -> RefreshTokenSchema | AccessTokenSchema:
        token_schema: AccessTokenSchema | RefreshTokenSchema = decode_and_verify_jwt(token)
        if token_schema.payload.type != token_type:
            raise MicroServiceError(status_code=403, detail="Неверный тип токена")
        return token_schema


