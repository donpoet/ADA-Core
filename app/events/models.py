from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, UTC

class Event(BaseModel):
    pass

class TaskExecutionCompletedEvent(Event):
    task_id: UUID
    task_execution_id: UUID
    task_result_id: UUID
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
