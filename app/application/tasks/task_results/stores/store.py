from abc import ABC, abstractmethod
from uuid import UUID

from app.tasks.models import TaskResult

class TaskResultStore(ABC):
    @abstractmethod
    def get_task_result(self, task_execution_id: UUID) -> TaskResult:
        pass

    def save_task_result(self, task_result: TaskResult) -> None:
        pass