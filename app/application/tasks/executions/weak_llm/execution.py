from app.tasks.models import TaskExecution, TaskResult
from app.artifacts.models import Artifact
from app.tasks.enums import TaskResultStatus
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.ollama.models import OllamaContextOutput
from app.ollama.model_provider import OllamaModelProvider
from app.application.artifacts.stores.artifact_store import ArtifactStore

from uuid import UUID

class WeakLLMTaskExecution(TaskExecution[OllamaContextOutput]):

    def __init__(
        self,
        task_id: UUID,
        context: OllamaContextOutput,
        artifact_store: ArtifactStore,
        model_provider: OllamaModelProvider):
        super().__init__(
            task_id=task_id,
            context=context,
            artifact_store=artifact_store
        )
        self._model_provider = model_provider

    async def execute(self) -> TaskResult:
        self.start()

        try:
            response = self._model_provider.chat(self.context)

            artifact = self._artifact_store.create_artifact(
                artifact_type=ArtifactType.LLM_RESPONSE,
                artifact_operation=ArtifactOperation.CREATE,
                reference=None,
                task_execution_id=self.id,
                data={
                    "content": response.content
                }
            )

            self.complete()
            return TaskResult(
                task_execution_id=self.id,
                status=TaskResultStatus.SUCCESS,
                error_code=None,
            )
        except Exception as error:
            self.fail()
            return TaskResult(
                task_execution_id=self.id,
                status=TaskResultStatus.FAILED,
                error_code=str(error.args),
            )