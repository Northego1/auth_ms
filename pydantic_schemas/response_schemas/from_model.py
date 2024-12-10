from typing import Self
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field



class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str = Field(max_length=32)
    hashed_password: bytes
    email: EmailStr
    is_active: bool = True