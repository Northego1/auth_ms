from typing import Type
from pydantic import BaseModel


class PayloadMessage(BaseModel):
    content: dict | BaseModel
    
