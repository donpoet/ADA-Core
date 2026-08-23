from .component_registry import TaskComponentRegistry
from .stores.store import TaskStore
from app.tasks.models import Task, TaskExecution

class TaskOrchestrator:

    def __init__(self, task_store: TaskStore, component_registry: TaskComponentRegistry):
        self._task_store = task_store
        self._component_registry = component_registry

    def execute(self, task: Task) -> TaskExecution:
        components = self._component_registry.get(task.type)
        context_input = components.context_input_provider.get(task)
        source = components.context_source_factory.create(context_input)
        context = components.context_builder.build(source)

        execution = components.execution_factory.create(
            task_id,
            context
        )

        self._task_store.save_task(task)

        await execution.execute()

        self._task_store.save_task_execution(execution)

        return execution