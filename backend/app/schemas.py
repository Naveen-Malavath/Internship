from __future__ import annotations

from datetime import datetime
from typing import Callable, List, Optional

from pydantic import BaseModel, EmailStr, Field


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.title() for word in parts[1:])


class CamelModel(BaseModel):
    class Config:
        alias_generator: Callable[[str], str] = to_camel
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}


class User(CamelModel):
    email: EmailStr
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginResponse(CamelModel):
    user: User
    message: str = "Login successful"


class Message(CamelModel):
    id: str
    content: str
    role: str = Field(regex="^(user|assistant)$")
    timestamp: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class Conversation(CamelModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationList(CamelModel):
    conversations: List[Conversation]
