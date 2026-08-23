from app.tasks.models import TaskExecution, TaskResult
from app.tasks.enums import TaskResultStatus
from app.ollama.models import OllamaContextOutput
from app.ollama.model_provider import OllamaModelProvider

from uuid import UUID

class WeakLLMTaskExecution(TaskExecution[OllamaContextOutput]):

    def __init__(
        self,
        task_id: UUID,
        context: OllamaContextOutput,
        model_provider: OllamaModelProvider):
        super().__init__(
            task_id=task_id,
            context=context,
        )
        self._model_provider = model_provider

    async def execute(self):
        self.start()

        try:
            response = await self._model_provider.chat(self.context)
            # TODO: create artifact from response
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
                error_code=str(type(error)),
            )