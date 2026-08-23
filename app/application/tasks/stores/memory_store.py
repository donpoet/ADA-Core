from uuid import uuid4, UUID

from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType
from .store import TaskStore
from app.context.models import ContextOutput

class InMemoryTaskStore(TaskStore):

    def __init__(self):
        self._tasks: dict[UUID, Task] = {}
        self._task_executions: dict[UUID, TaskExecution] = {}

    def create_task(self, task_type: TaskType, conversation_id: UUID,) -> Task:
        task = Task(
            type=task_type,
            conversation_id=conversation_id,
        )
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: UUID) -> Task:
        return self._tasks.get(task_id)

    def save_task(self, task: Task) -> None:
        self._tasks[task.id] = task 

    def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    
    def get_task_execution(self, task_execution_id: UUID) -> TaskExecution:
        return self._task_executions.get(task_execution_id)

    
    def save_task_execution(self, task_execution:TaskExecution) -> None:
        self._task_executions[task_execution.id] = task_execution

    
    def list_task_executions(self, task_id: UUID) -> list[TaskExecution]:
        task_executions = []
        for task_execution in self._task_executions.values():
            if task_execution.task_id == task_id:
                task_executions.append(task_execution)
        return task_executions