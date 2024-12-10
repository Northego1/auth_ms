import pickle
from typing import Self
from aio_pika import IncomingMessage
from pydantic import BaseModel


class DefaultRequestDto(BaseModel):
    @classmethod
    def from_message(cls, message: IncomingMessage) -> Self:
        message_body = pickle.loads(message.body)
        return cls(**message_body)