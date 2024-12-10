import json
from typing import Self
import uuid
from aio_pika import Message
from pydantic import BaseModel

from pydantic_schemas.message_schema import PayloadMessage



class CustomMessage(Message):
    def __init__(
            self: Self,
            body: BaseModel | dict,
            **kwargs
    ):
        payload = self._convert(body)
        super().__init__(body=payload, **kwargs)



    def _convert(self: Self, body: PayloadMessage | dict) -> bytes:
        if isinstance(body, BaseModel):
            return body.model_dump_json().encode()
        return json.dumps(body).encode()



