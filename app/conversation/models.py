from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime, UTC

from .enums import MessageRole

class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: MessageRole
    content: str

class Conversation(BaseModel): 
    id: UUID = Field(default_factory=uuid4)
    title: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    messages: list[Message] = Field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)

    def remove_system_message(self, message: Message):
        if message.role != MessageRole.SYSTEM:
            raise ValueError(
                f"Message {message.id} is not of Role 'System'"
            )
        self.messages.remove(message)