from sqlalchemy.orm import Session

from app.tasks.models import TaskResult
from app.tasks.enums import TaskResultStatus

from .store import TaskResultStore

from app.database.schema import TaskExecutionModel, TaskResultModel

from uuid import UUID

class SQLiteTaskResultStore(TaskResultStore):

    def __init__(self, engine):
        self._engine = engine

    def get_task_result(self, task_execution_id: UUID) -> TaskResult | None:
        with Session(self._engine) as session:
            task_execution_model = session.get(
                TaskExecutionModel,
                str(task_execution_id)
            )

            if task_execution_model is None:
                raise ValueError(
                    f"TaskExecution {task_execution_id} not found"
                )
            
            task_result_model = task_execution_model.result

            if task_result_model is None:
                return None

            return TaskResult(
                id=UUID(task_result_model.id),
                task_execution_id=task_result_model.task_execution_id,
                status=task_result_model.status,
                error_code=task_result_model.error_code,
            )

    def save_task_result(self, task_result: TaskResult) -> None:
        with Session(self._engine) as session:
            task_execution_model = session.get(
                TaskExecutionModel,
                str(task_result.task_execution_id)
            )
            if task_execution_model is None:
                raise ValueError(
                    f"TaskExecution {task_result.task_execution_id} not found"
                )

            if task_execution_model.result is not None:
                raise DuplicateTaskResultError(
                    f"TaskResult for TaskExecution {task_result.task_execution_id} already exists"
                )

            session.add(
                TaskResultModel(
                    id=str(task_result.id),
                    task_execution_id=str(task_result.task_execution_id),
                    status=task_result.status,
                    error_code=task_result.error_code,
                )
            )
            session.commit()


class DuplicateTaskResultError(Exception):
    pass