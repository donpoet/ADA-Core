from app.application.tasks.execution_factory import TaskExecutionFactory
from app.ollama.models import OllamaContextOutput
from .execution import WeakLLMTaskExecution
from app.chat.service import ChatService

class WeakLLMTaskExecutionFactory(TaskExecutionFactory[OllamaContextOutput]):
    def create(self, task_id: UUID, context: OllamaContextOutput) -> TaskExecution:
        return WeakLLMTaskExecution(context=context, task_id=task_id)