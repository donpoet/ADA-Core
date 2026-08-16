from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ChatRequest(BaseModel):
    prompt: str
    conversation_id: UUID | None = None

class ChatResponse(BaseModel): 
    response: str
    conversation_id: UUID

class ConversationListItem(BaseModel):
    id: UUID
    title: str | None = None
    created_at: datetime
    updated_at: datetime

class ConversationsListResponse(BaseModel):
    conversations: list[ConversationListItem]  