from .store import TaskStore

from app.tasks.enums import TaskType
from app.tasks.models import Task

from app.database.schema import TaskModel, TaskMessageModel

from uuid import UUID
from sqlalchemy.orm import Session

from app.database.utils import ensure_utc


class SQLiteTaskStore(TaskStore):

    def __init__(self, engine):
        self._engine = engine

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
        pass

    
    def save_task_execution(self, task_execution:TaskExecution) -> None:
        pass

    
    def list_task_executions(self, task_id: UUID) -> list[TaskExecution]:
        pass