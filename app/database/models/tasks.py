from datetime import datetime

from sqlalchemy import Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conversations import ConversationModel, MessageModel

from app.database.database import Base

from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus, TaskResultStatus

from app.artifacts.enums import ArtifactOperation, ArtifactType

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id"),
        nullable=False,
    )

    conversation: Mapped["ConversationModel"] = relationship(
        back_populates="tasks"
    )

    type: Mapped[TaskType] = mapped_column(
        Enum(TaskType),
        nullable=False,
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    executions: Mapped[list["TaskExecutionModel"]] = relationship(
        back_populates="task",
    )

    source_messages: Mapped[list["TaskMessageModel"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )


class TaskExecutionModel(Base):
    __tablename__ = "task_executions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id"),
        nullable=False,
    )

    task: Mapped["TaskModel"] = relationship(
        back_populates="executions"
    )

    status: Mapped[TaskExecutionStatus] = mapped_column(
        Enum(TaskExecutionStatus),
        nullable=False,
    )

    context: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    result: Mapped["TaskResultModel"] = relationship(
        back_populates="execution"
    )

    artifacts: Mapped[list["ArtifactModel"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
    )

class TaskResultModel(Base):
    __tablename__ = "task_results"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    task_execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("task_executions.id"),
        nullable=False,
        unique=True,
    )

    execution: Mapped["TaskExecutionModel"] = relationship(
        back_populates="result"
    )

    status: Mapped[TaskResultStatus] = mapped_column(
        Enum(TaskResultStatus),
        nullable=False,
    )

    error_code: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

class TaskMessageModel(Base):
    __tablename__ = "task_messages"

    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id"),
        nullable=False,
        primary_key=True
    )

    task: Mapped["TaskModel"] = relationship(
        back_populates="source_messages"
    )

    message_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("messages.id"),
        nullable=False,
        primary_key=True,
    )

    message: Mapped["MessageModel"] = relationship(
        back_populates="task_links"
    )

class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        nullable=False,
    )

    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType),
        nullable=False,
    )

    operation: Mapped[ArtifactOperation] = mapped_column(
        Enum(ArtifactOperation),
        nullable=False,
    )

    reference: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    task_execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("task_executions.id"),
        nullable=False,
    )

    execution: Mapped["TaskExecutionModel"] = relationship(
        back_populates="artifacts",
    )

    data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )