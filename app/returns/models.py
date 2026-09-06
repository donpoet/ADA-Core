from .enums import ReturnAction
from pydantic import BaseModel
from app.context.models import ContextSource
from app.tasks.models import Task, TaskResult
from app.artifacts.models import Artifact
from app.conversation.models import Conversation

class ReturnDecision(BaseModel):
    action: ReturnAction

class ReturnContextSource(ContextSource, BaseModel):
    task: Task
    task_result: TaskResult
    artifacts: list[Artifact]
    conversation: Conversation