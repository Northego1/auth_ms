
from typing import Self
from pydantic import BaseModel

from api.v1.utils.custom_message import CustomMessage
from pydantic_schemas.message_schema import PayloadMessage


class DefaultMicroServiceResponseSchema(BaseModel):
    """Default response from microservices"""
    status_code: int
    detail: str | None = None


    def to_message(self: Self) -> CustomMessage:
        return CustomMessage(body=self)
