from abc import ABC, abstractmethod
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType, TaskStatus
from app.context.models import ContextOutput
from uuid import UUID
from datetime import datetime

class TaskStore(ABC):

    @abstractmethod
    def create_task(self, task_type: TaskType, conversation_id: UUID) -> Task:
        pass

    @abstractmethod
    def get_task(self, task_id: UUID) -> Task:
        pass

    @abstractmethod
    def save_task(self, task:Task) -> None:
        pass

    @abstractmethod
    def list_tasks(self) -> list[Task]:
        pass

    @abstractmethod
    def filter_tasks(
        self,
        *,
        conversation_id: UUID | None = None,
        task_type: TaskType | None = None,
        status: TaskStatus | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        completed_before: datetime | None = None,
        completed_after: datetime | None = None
    ) -> list[Task]:
        pass

    @abstractmethod
    def get_task_execution(self, task_execution_id: UUID) -> TaskExecution:
        pass

    @abstractmethod
    def save_task_execution(self, task_execution:TaskExecution) -> None:
        pass

    @abstractmethod
    def list_task_executions(self, task_id: UUID) -> list[TaskExecution]:
        pass