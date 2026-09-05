from pydantic import BaseModel
from .enums import IntentAction
from app.tasks.enums import TaskType
from app.conversation.models import Conversation, Message
from app.context.models import ContextSource, ContextInput, ContextOutput

from uuid import UUID

class Intent(BaseModel):
    intent_action: IntentAction
    task_type: TaskType | None = None 
    source_message_id: UUID | None = None

class IntentContextSource(BaseModel, ContextSource):
    conversation: Conversation
    task_types: list[TaskType]
    intent_actions: list[IntentAction]