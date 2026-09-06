from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.component_registry import TaskComponentRegistry
from app.application.tasks.components import TaskComponents
from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.application.tasks.task_results.stores.memory_store import InMemoryTaskResultStore
from app.application.artifacts.stores.artifact_memory_store import InMemoryArtifactStore
from app.tasks.models import TaskExecution, TaskResult
from app.tasks.enums import TaskType, TaskExecutionStatus, TaskStatus, TaskResultStatus

from app.context.context_source_factory import ContextSourceFactory
from app.context.context_input_provider import ContextInputProvider
from app.context.context import ContextBuilder
from app.application.tasks.execution_factory import TaskExecutionFactory
from app.events.event_publisher import EventPublisher
from app.events.models import TaskExecutionCompletedEvent

from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

class SuccessfulTestTaskExection(TaskExecution):
    async def execute(self) -> TaskResult:
        self.start()
        self.complete()
        return TaskResult(
            id=uuid4(),
            task_execution_id=self.id,
            status=TaskResultStatus.SUCCESS
        )

class FailedTestTaskExection(TaskExecution):
    async def execute(self):
        self.start()
        self.fail()
        return TaskResult(
            id=uuid4(),
            task_execution_id=self.id,
            status=TaskResultStatus.FAILED
        )

@pytest.mark.asyncio
async def test_excute_successful_execution():
    task_component_registry = TaskComponentRegistry()
    task_store = InMemoryTaskStore()
    task_result_store = InMemoryTaskResultStore()
    artifact_store = InMemoryArtifactStore()

    task = task_store.create_task(
        TaskType.WEAK_LLM,
        conversation_id=uuid4()
    )

    context_source_factory = AsyncMock(ContextSourceFactory)
    context_source_factory.create.return_value = None

    context_builder = AsyncMock(ContextBuilder)
    context_builder.build.return_value = None

    task_execution_factory = AsyncMock(TaskExecutionFactory)
    task_execution_factory.create.return_value = SuccessfulTestTaskExection(
        task_id=task.id,
        context = {},
        artifact_store=artifact_store,
    )

    context_input_provider = AsyncMock(ContextInputProvider)
    context_input_provider.get.return_value = None


    task_component_registry.register(
        TaskType.WEAK_LLM,
        TaskComponents(
            context_source_factory=context_source_factory,
            context_builder=context_builder,
            execution_factory=task_execution_factory,
            context_input_provider=context_input_provider
        )
    )

    event_publisher = AsyncMock(EventPublisher)

    task_orchestrator = TaskOrchestrator(task_store, task_component_registry, task_result_store, event_publisher)

    execution = await task_orchestrator.execute(task)

    assert execution.status == TaskExecutionStatus.COMPLETED
    assert task.status == TaskStatus.COMPLETED

    task_result = task_result_store.get_task_result(execution.id)

    assert task_result is not None
    assert task_result.status == TaskResultStatus.SUCCESS

    stored_execution = task_store.get_task_execution(
        execution.id
    )

    assert isinstance(stored_execution, TaskExecution)

    published_event = event_publisher.publish_event.await_args.args[0]
    
    assert isinstance(published_event, TaskExecutionCompletedEvent)
    assert published_event.task_id == task.id
    assert published_event.task_execution_id == execution.id
    assert published_event.task_result_id == task_result.id

    

@pytest.mark.asyncio
async def test_excute_failed_execution():
    task_component_registry = TaskComponentRegistry()
    task_store = InMemoryTaskStore()
    task_result_store = InMemoryTaskResultStore()
    artifact_store = InMemoryArtifactStore()

    task = task_store.create_task(
        TaskType.WEAK_LLM,
        conversation_id=uuid4()
    )

    context_source_factory = AsyncMock(ContextSourceFactory)
    context_source_factory.create.return_value = None

    context_builder = AsyncMock(ContextBuilder)
    context_builder.build.return_value = None

    task_execution_factory = AsyncMock(TaskExecutionFactory)
    task_execution_factory.create.return_value = FailedTestTaskExection(
        task_id=task.id,
        context = {},
        artifact_store=artifact_store,
    )

    context_input_provider = AsyncMock(ContextInputProvider)
    context_input_provider.get.return_value = None


    task_component_registry.register(
        TaskType.WEAK_LLM,
        TaskComponents(
            context_source_factory=context_source_factory,
            context_builder=context_builder,
            execution_factory=task_execution_factory,
            context_input_provider=context_input_provider
        )
    )

    event_publisher = AsyncMock(EventPublisher)

    task_orchestrator = TaskOrchestrator(task_store, task_component_registry, task_result_store, event_publisher)

    execution = await task_orchestrator.execute(task)

    assert execution.status == TaskExecutionStatus.FAILED
    assert task.status == TaskStatus.OPEN
    
    task_result = task_result_store.get_task_result(execution.id)

    assert task_result is not None
    assert task_result.status == TaskResultStatus.FAILED
    
    published_event = event_publisher.publish_event.await_args.args[0]

    assert isinstance(published_event, TaskExecutionCompletedEvent)
    assert published_event.task_id == task.id
    assert published_event.task_execution_id == execution.id
    assert published_event.task_result_id == task_result.id
