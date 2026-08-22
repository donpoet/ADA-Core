from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, UTC
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus, TaskResultStatus

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    type: TaskType
    status: TaskStatus = TaskStatus.OPEN
    source_message_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory= lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def cancel(self) -> None:
        if(self.status != TaskStatus.OPEN):
            raise InvalidTaskStateError(
                f"Cannot cancel task in status {self.status}"
            )
        self.status = TaskStatus.CANCELLED
    
    def complete(self) -> None:
        if(self.status != TaskStatus.OPEN):
            raise InvalidTaskStateError(
                f"Cannot complete task in status {self.status}"
            )
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

class InvalidTaskStateError(Exception):
    pass

class InvalidTaskExecutionStateError(Exception):
    pass

class TaskResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task_execution_id: UUID
    status: TaskResultStatus
    error_code: str | None = None

I = TypeVar("I")

class TaskExecution(ABC, BaseModel, Generic[I]):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    status: TaskExecutionStatus = TaskExecutionStatus.PENDING
    context: I
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    @abstractmethod
    def execute(self) -> TaskResult:
        pass

    def start(self) -> None:
        if (self.status != TaskExecutionStatus.PENDING):
            raise InvalidTaskExecutionStateError(
                f"Cannot start execution with status: {self.status}"
            )
        self.status = TaskExecutionStatus.RUNNING

    def complete(self) -> None:
        if (self.status != TaskExecutionStatus.RUNNING):
            raise InvalidTaskExecutionStateError(
                f"Cannot complete non-running execution. Status: {self.status}"
            )
        self.status = TaskExecutionStatus.COMPLETED
        self.finished_at = datetime.now(UTC)

    def cancel(self) -> None:
        if (self.status != TaskExecutionStatus.RUNNING and self.status != TaskExecutionStatus.PENDING):
            raise InvalidTaskExecutionStateError(
                f"Cannot cancel non-running or non-pending execution. Status: {self.status}"
            )
        self.status = TaskExecutionStatus.CANCELLED
        self.finished_at = datetime.now(UTC)

    def fail(self) -> None:
        if (self.status != TaskExecutionStatus.RUNNING):
            raise InvalidTaskExecutionStateError(
                f"Cannot fail non-running execution. Status: {self.status}"
            )
        self.status = TaskExecutionStatus.FAILED
        self.finished_at = datetime.now(UTC)
