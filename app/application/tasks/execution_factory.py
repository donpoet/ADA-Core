from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from app.tasks.models import TaskExecution

C = TypeVar("C")

class TaskExecutionFactory(ABC, Generic[C]):

    @abstractmethod
    def create(self, task_id: UUID, context: C) -> TaskExecution:
        pass