from app.tasks.enums import TaskType

from .components import TaskComponents

class TaskComponentRegistry:

    def __init__(self):
        self._components: dict[TaskType, TaskComponents] = {}

    def register(self, task_type: TaskType, components: TaskComponents) -> None:
        self._components[task_type] = components

    def get(self, task_type: TaskType) -> TaskComponents:
        return self._components[task_type]