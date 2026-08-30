from .store import TaskStore

from app.tasks.enums import TaskType
from app.tasks.models import Task, TaskExecution, TaskResult
from app.application.artifacts.stores.artifact_store import ArtifactStore

from app.application.tasks.component_registry import TaskComponentRegistry

from app.database.schema import (
    TaskModel,
    TaskMessageModel,
    TaskExecutionModel,
    TaskResultModel
)

from uuid import UUID
from sqlalchemy.orm import Session

from app.database.utils import ensure_utc


class SQLiteTaskStore(TaskStore):

    def __init__(self, engine, task_component_registry: TaskComponentRegistry):
        self._engine = engine
        self._task_component_registry = task_component_registry

    def create_task(self, task_type: TaskType, conversation_id: UUID) -> Task:
        task = Task(
            conversation_id=conversation_id,
            type=task_type,
        ) 

        db_task = TaskModel(
            id=str(task.id),
            conversation_id=str(task.conversation_id),
            type=task.type,
            status=task.status,   
            created_at=ensure_utc(task.created_at)     
        )

        with Session(self._engine) as session:
            session.add(db_task)
            session.commit()
        
        return task

    def get_task(self, task_id: UUID) -> Task:
        with Session(self._engine) as session:
            result = session.get(
                TaskModel,
                str(task_id),
            )

            if result is None:
                raise ValueError(
                    f"Task {task_id} not found"
                )
            
            return Task(
                id=UUID(result.id),
                conversation_id=UUID(result.conversation_id),
                type=result.type,
                status=result.status,
                source_message_ids=[
                    UUID(task_message.message_id)
                    for task_message in result.source_messages
                ],
                created_at=ensure_utc(result.created_at),
                completed_at=(
                    ensure_utc(result.completed_at) 
                    if result.completed_at is not None
                    else None
                ),
            )

    def save_task(self, task: Task) -> None:
        with Session(self._engine) as session:
            task_model = session.get(
                TaskModel,
                str(task.id),
            )

            if task_model is None:
                task_model = TaskModel(
                    id=str(task.id),
                    conversation_id=str(task.conversation_id),
                    type=task.type,
                    status=task.status,
                    source_messages=self.resolve_source_messages(task, session),   
                    created_at=ensure_utc(task.created_at),
                    completed_at=(
                        ensure_utc(task.completed_at)
                        if task.completed_at is not None
                        else None
                    ),     
                )
                session.add(task_model)
            
            task_model.conversation_id = str(task.conversation_id)
            task_model.type = task.type
            task_model.status = task.status
            task_model.source_messages = self.resolve_source_messages(task, session)
            task_model.created_at=ensure_utc(task.created_at)
            task_model.completed_at = (
                    ensure_utc(task.completed_at)
                    if task.completed_at is not None
                    else None
                )

            session.commit()

    def list_tasks(self) -> list[Task]:
        tasks: list[Task] = []
        with Session(self._engine) as session:
            task_models = session.query(TaskModel).all()

            for task_model in task_models:

                tasks.append(
                    Task(
                        id=UUID(task_model.id),
                        conversation_id=UUID(task_model.conversation_id),
                        type=task_model.type,
                        status=task_model.status,
                        source_message_ids=[
                            UUID(task_message.message_id)
                            for task_message in task_model.source_messages
                        ],
                        created_at=ensure_utc(task_model.created_at),
                        completed_at=(
                            ensure_utc(task_model.completed_at) 
                            if task_model.completed_at is not None
                            else None
                        ),
                    )
                )
        return tasks

    def filter_tasks(
        self,
        *,
        conversation_id: UUID | None = None,
        task_type: TaskType | None = None,
        status: TaskStatus | None = None,
        created_before: datetime | None = None,
        created_after: datetime | None = None,
        completed_before: datetime | None = None,
        completed_after: datetime | None = None,
        ) -> list[Task]:
        tasks: list[Task] = []
        with Session(self._engine) as session:
            query = session.query(TaskModel)

            if conversation_id is not None:
                query = query.where(
                    TaskModel.conversation_id == str(conversation_id)
                )

            if task_type is not None:
                query = query.where(
                    TaskModel.type == task_type
                )

            if status is not None:
                query = query.where(
                    TaskModel.status == status
                )

            if created_before is not None:
                query = query.where(
                    TaskModel.created_at < created_before
                )

            if created_after is not None:
                query = query.where(
                    TaskModel.created_at >= created_after
                )
            
            if completed_before is not None:
                query = query.where(
                    TaskModel.completed_at is not None and TaskModel.completed_at < completed_before
                )

            if completed_after is not None:
                query = query.where(
                    TaskModel.completed_at is not None and TaskModel.completed_at >= completed_after
                )

            task_models = query.all()

            for task_model in task_models:

                tasks.append(
                    Task(
                        id=UUID(task_model.id),
                        conversation_id=UUID(task_model.conversation_id),
                        type=task_model.type,
                        status=task_model.status,
                        source_message_ids=[
                            UUID(task_message.message_id)
                            for task_message in task_model.source_messages
                        ],
                        created_at=ensure_utc(task_model.created_at),
                        completed_at=(
                            ensure_utc(task_model.completed_at) 
                            if task_model.completed_at is not None
                            else None
                        ),
                    )
                )
        return tasks



    def resolve_source_messages(self, task: Task, session: Session) -> list[TaskMessageModel]:
        source_messages: list[TaskMessageModel] = []
        
        for message_id in task.source_message_ids:
            task_message = session.get(
                TaskMessageModel,
                (str(task.id), str(message_id)), # Composite Key as Tuple
            )
            if task_message is None:
                task_message = TaskMessageModel(
                        task_id=str(task.id),
                        message_id=str(message_id)
                    )
                session.add(task_message)
            
            source_messages.append(task_message)
        
        return source_messages

        
    def get_task_execution(self, task_execution_id: UUID) -> TaskExecution:
        with Session(self._engine) as session:
            task_execution_model = session.get(
                TaskExecutionModel,
                str(task_execution_id),
            )

            if task_execution_model is None:
                raise ValueError(
                    f"TaskExecution {task_execution_id} not found"
                )

            task_model = task_execution_model.task

            task_execution_factory = self._task_component_registry.get(task_model.type).execution_factory

            return task_execution_factory.build(
                id=UUID(task_execution_model.id),
                task_id=UUID(task_execution_model.task_id),
                status=task_execution_model.status,
                context=task_execution_model.context,
                started_at=(
                    ensure_utc(task_execution_model.started_at)
                    if task_execution_model.started_at is not None
                    else None
                ),
                finished_at=(
                    ensure_utc(task_execution_model.finished_at)
                    if task_execution_model.finished_at is not None
                    else None
                ),
            )

    
    def save_task_execution(self, task_execution:TaskExecution) -> None:
        with Session(self._engine) as session:
            task_execution_model = session.get(
                TaskExecutionModel,
                str(task_execution.id),
            )

            if task_execution_model is None:
                task_execution_model = TaskExecutionModel(
                    id=str(task_execution.id),
                    task_id=str(task_execution.task_id),
                    status=task_execution.status,
                    context=task_execution.context.model_dump(),
                    started_at=(
                        ensure_utc(task_execution.started_at)
                        if task_execution.started_at is not None
                        else None
                    ),
                    finished_at=(
                        ensure_utc(task_execution.finished_at)
                        if task_execution.finished_at is not None
                        else None
                    ),
                )
                session.add(task_execution_model)
            
            task_execution_model.task_id = str(task_execution.task_id)
            task_execution_model.status = task_execution.status
            task_execution_model.context = task_execution.context.model_dump()
            task_execution_model.started_at =(
                        ensure_utc(task_execution.started_at)
                        if task_execution.started_at is not None
                        else None
                    )
            task_execution_model.finished_at =(
                        ensure_utc(task_execution.finished_at)
                        if task_execution.finished_at is not None
                        else None
                    )
            
            session.commit()



    
    def list_task_executions(self, task_id: UUID) -> list[TaskExecution]:
        task_executions: list[TaskExecution] = []
        with Session(self._engine) as session:
            task_model = session.get(
                TaskModel,
                str(task_id),
            )

            if task_model is None:
                raise ValueError(
                    f"Task {task_id} not found"
                )

            task_execution_factory = self._task_component_registry.get(task_model.type).execution_factory
            
            for task_execution_model in task_model.executions:
                task_executions.append(
                    task_execution_factory.build(
                        id=UUID(task_execution_model.id),
                        task_id=UUID(task_execution_model.task_id),
                        status=task_execution_model.status,
                        context=task_execution_model.context,
                        started_at=(
                            ensure_utc(task_execution_model.started_at)
                            if task_execution_model.started_at is not None
                            else None
                        ),
                        finished_at=(
                            ensure_utc(task_execution_model.finished_at)
                            if task_execution_model.finished_at is not None
                            else None
                        ),
                    )
                )
        
        return task_executions
            
