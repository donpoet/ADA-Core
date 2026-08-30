from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.component_registry import TaskComponentRegistry
from app.application.tasks.components import TaskComponents
from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.tasks.task_results.stores.sqlite_store import SQLiteTaskResultStore
from app.application.artifacts.stores.artifact_sqlite_store import SQLiteArtifactStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.tasks.models import TaskExecution, TaskResult
from app.tasks.enums import TaskType, TaskExecutionStatus, TaskStatus, TaskResultStatus

from app.context.context_source_factory import ContextSourceFactory
from app.context.context_input_provider import ContextInputProvider
from app.context.context import ContextBuilder
from app.application.tasks.execution_factory import TaskExecutionFactory

from uuid import uuid4
from unittest.mock import Mock

import pytest

from pydantic import BaseModel

class SuccessfulTestTaskExection(TaskExecution):
    async def execute(self) -> TaskResult:
        self.start()
        self.complete()
        return TaskResult(
            id=uuid4(),
            task_execution_id=self.id,
            status=TaskResultStatus.SUCCESS
        )

class TestContext(BaseModel):
    content: str

@pytest.mark.asyncio
async def test_excute_successful_execution(db_engine):
    task_component_registry = TaskComponentRegistry()
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    task_result_store = SQLiteTaskResultStore(db_engine)
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)

    conversation = conversation_store.create()

    task = task_store.create_task(
        TaskType.WEAK_LLM,
        conversation_id=conversation.id
    )

    context_source_factory = Mock(ContextSourceFactory)
    context_source_factory.create.return_value = None

    context_builder = Mock(ContextBuilder)
    context_builder.build.return_value = None

    task_execution_factory = Mock(TaskExecutionFactory)
    task_execution_factory.create.return_value = SuccessfulTestTaskExection(
        task_id=task.id,
        context=TestContext(content="context"),
        artifact_store=artifact_store,
    )

    context_input_provider = Mock(ContextInputProvider)
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

    task_orchestrator = TaskOrchestrator(task_store, task_component_registry, task_result_store)

    execution = await task_orchestrator.execute(task)

    task_execution_factory.build.return_value = SuccessfulTestTaskExection(
        id=execution.id,
        task_id=execution.task_id,
        status=execution.status,
        context=TestContext(content="context"),
        artifact_store=artifact_store,
        started_at=execution.started_at,
        finished_at=execution.finished_at,
    )

    assert execution.status == TaskExecutionStatus.COMPLETED
    assert task.status == TaskStatus.COMPLETED

    task_result = task_result_store.get_task_result(execution.id)

    assert task_result is not None
    assert task_result.status == TaskResultStatus.SUCCESS

    stored_execution = task_store.get_task_execution(
        execution.id
    )
    assert isinstance(stored_execution, TaskExecution)

    stored_task = task_store.get_task(task.id)
    assert stored_task.status == TaskStatus.COMPLETED