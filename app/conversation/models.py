from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4, UUID

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: MessageRole
    content: str

class Conversation(BaseModel): 
    id: UUID = Field(default_factory=uuid4)
    messages: list[Message] = Field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)