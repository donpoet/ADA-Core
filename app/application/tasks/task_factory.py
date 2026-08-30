from app.tasks.models import Task
from app.tasks.enums import TaskType
from app.application.tasks.stores.store import TaskStore
from uuid import UUID

class TaskFactory():
    def __init__(self, task_store: TaskStore):
        self._task_store = task_store

    def create_task(self, task_type: TaskType, conversation_id: UUID, source_message_id: UUID) -> Task:
        task = self._task_store.create_task(task_type, conversation_id)
        task.source_message_ids.append(source_message_id)
        self._task_store.save_task(task)

        return task

    def update_task(self, task: Task, source_message_id: UUID) -> Task:
        task.source_message_ids.append(source_message_id)
        self._task_store.save_task(task)

        return task