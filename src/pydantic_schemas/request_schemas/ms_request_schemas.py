from re import L
from pydantic import EmailStr, Field

from pydantic_schemas.request_schemas.base_request_schema import DefaultRequestDto




class MsRequestLoginDto(DefaultRequestDto):
    username: str = Field(max_length=32)
    hashed_password: bytes
    fingerprint: bytes
    

class MsRequestRegisterDto(DefaultRequestDto):
    username: str = Field(max_length=32)
    hashed_password: bytes
    email: EmailStr


class MsRequestRefreshJwtDto(DefaultRequestDto):
    fingerprint: bytes
    refresh_token: str


class MsRequestLogoutDto(DefaultRequestDto):
    access_token: str
    refresh_token: str | None
    fingerprint: bytes


class UserUpdateRequestSchema:
    pass


class UserDeleteRequestSchema:
    pass