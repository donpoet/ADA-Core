from .component_registry import TaskComponentRegistry
from .stores.store import TaskStore
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskExecutionStatus, TaskStatus
from app.application.tasks.task_results.stores.store import TaskResultStore
from app.events.event_publisher import EventPublisher
from app.events.models import TaskExecutionCompletedEvent

class TaskOrchestrator:

    def __init__(self, task_store: TaskStore, component_registry: TaskComponentRegistry, task_result_store: TaskResultStore, event_publisher: EventPublisher):
        self._task_store = task_store
        self._component_registry = component_registry
        self._task_result_store = task_result_store
        self._event_publisher = event_publisher

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

        await self._event_publisher.publish_event(
            TaskExecutionCompletedEvent(
                task_id=task.id,
                task_execution_id=execution.id,
                task_result_id=result.id
            )
        )

        return execution