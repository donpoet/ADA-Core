from pydantic import BaseModel
from .enums import IntentAction
from app.tasks.enums import TaskType

from uuid import UUID

class Intent(BaseModel):
    intent_action: IntentAction
    task_type: TaskType | None = None 
    source_message_id: UUID | None = None