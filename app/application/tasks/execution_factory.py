from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID
from datetime import datetime

from app.tasks.models import TaskExecution
from app.tasks.enums import TaskExecutionStatus
from app.application.artifacts.stores.artifact_store import ArtifactStore

C = TypeVar("C")

class TaskExecutionFactory(ABC, Generic[C]):

    def __init__(self, artifact_store: ArtifactStore):
        self._artifact_store = artifact_store

    @abstractmethod
    def create(self, task_id: UUID, context: C) -> TaskExecution:
        pass

    @abstractmethod
    def build(self, id:UUID, task_id: UUID, status: TaskExecutionStatus, context: C, started_at: datetime | None = None, finished_at:datetime | None = None):
        pass