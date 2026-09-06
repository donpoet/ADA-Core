from app.context.context_source_factory import ContextSourceFactory
from app.returns.models import ReturnContextSource
from app.events.models import TaskExecutionCompletedEvent
from app.application.tasks.stores.store import TaskStore
from app.application.tasks.task_results.stores.store import TaskResultStore
from app.application.artifacts.stores.artifact_store import ArtifactStore
from app.application.conversations.stores.store import ConversationStore

class TaskExecutionCompletedReturnContextSourceFactory(ContextSourceFactory[TaskExecutionCompletedEvent, ReturnContextSource]):
    def __init__(
        self,
        task_store: TaskStore,
        task_result_store: TaskResultStore,
        artifact_store: ArtifactStore,
        conversation_store: ConversationStore,
    ):
        self._task_store = task_store
        self._task_result_store = task_result_store
        self._artifact_store = artifact_store
        self._conversation_store = conversation_store

    def create(self, event: TaskExecutionCompletedEvent) -> ReturnContextSource:
        task = self._task_store.get_task(event.task_id)
        task_result = self._task_result_store.get_task_result(event.task_execution_id)
        artifacts = self._artifact_store.list_artifacts(event.task_execution_id)
        conversation = self._conversation_store.get(task.conversation_id)

        return ReturnContextSource(
            task=task,
            task_result=task_result,
            artifacts=artifacts,
            conversation=conversation
        )