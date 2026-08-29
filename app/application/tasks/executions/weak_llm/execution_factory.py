from app.application.tasks.execution_factory import TaskExecutionFactory
from app.ollama.models import OllamaContextOutput
from .execution import WeakLLMTaskExecution
from app.chat.service import ChatService
from app.application.artifacts.stores.artifact_store import ArtifactStore
from app.llm_models.provider import ModelProvider
from datetime import datetime

class WeakLLMTaskExecutionFactory(TaskExecutionFactory[OllamaContextOutput]):
    def __init__(self, artifact_store: ArtifactStore, model_provider: ModelProvider):
        super().__init__(artifact_store)
        self._model_provider = model_provider

    def create(self, task_id: UUID, context: OllamaContextOutput) -> TaskExecution:
        return WeakLLMTaskExecution(context=context, task_id=task_id, artifact_store=self._artifact_store, model_provider=self._model_provider)

    def build(self, id:UUID, task_id: UUID, status: TaskExecutionStatus, context: OllamaContextOutput, started_at: datetime | None = None, finished_at:datetime | None = None):
         return WeakLLMTaskExecution(
            id=id,
            task_id=task_id,
            status=status,
            context=OllamaContextOutput(
                **context
            ),
            started_at=started_at,
            finished_at=finished_at,
            artifact_store=self._artifact_store,
            model_provider=self._model_provider,
            )
