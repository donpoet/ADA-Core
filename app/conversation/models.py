from enum import Enum
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str

class Conversation(BaseModel): 
    messages: list[Message] = Field(default_factory=list)