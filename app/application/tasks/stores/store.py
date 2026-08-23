from abc import ABC, abstractmethod
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType
from app.context.models import ContextOutput
from uuid import UUID

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
    def get_task_execution(self, task_execution_id: UUID) -> TaskExecution:
        pass

    @abstractmethod
    def save_task_execution(self, task_execution:TaskExecution) -> None:
        pass

    @abstractmethod
    def list_task_executions(self, task_id: UUID) -> list[TaskExecution]:
        pass