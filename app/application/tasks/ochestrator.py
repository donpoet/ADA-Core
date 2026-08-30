from .component_registry import TaskComponentRegistry
from .stores.store import TaskStore
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskExecutionStatus, TaskStatus
from app.application.tasks.task_results.stores.store import TaskResultStore

class TaskOrchestrator:

    def __init__(self, task_store: TaskStore, component_registry: TaskComponentRegistry, task_result_store: TaskResultStore):
        self._task_store = task_store
        self._component_registry = component_registry
        self._task_result_store = task_result_store

    async def execute(self, task: Task) -> TaskExecution:
        components = self._component_registry.get(task.type)
        context_input = components.context_input_provider.get(task)
        source = components.context_source_factory.create(context_input)
        context = components.context_builder.build(source)

        execution = components.execution_factory.create(
            task.id,
            context
        )

        self._task_store.save_task_execution(execution)

        result = await execution.execute()
        self._task_result_store.save_task_result(result)

        self._task_store.save_task_execution(execution)

        if execution.status == TaskExecutionStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            self._task_store.save_task(task)

        return execution