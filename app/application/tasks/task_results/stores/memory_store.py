from .store import TaskResultStore
from app.tasks.models import TaskResult
from uuid import uuid4, UUID

class InMemoryTaskResultStore(TaskResultStore):

    def __init__(self):
        self._task_results: dict[UUID, TaskResult] = {}

    def get_task_result(self, task_execution_id: UUID) -> TaskResult:
        return self._task_results.get(task_execution_id)

    def save_task_result(self, task_result: TaskResult) -> None:
        self._task_results[task_result.task_execution_id] = task_result