import pytest

from app.conversation.memory_store import InMemoryConversationStore
from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.application.artifacts.stores.artifact_memory_store import InMemoryArtifactStore
from app.llm_models.provider import ModelProvider
from app.ollama.models import OllamaModelOutput
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.application.tasks.component_registry import TaskComponentRegistry
from app.ollama.context_builder import OllamaContextBuilder
from app.application.tasks.executions.weak_llm.execution_factory import WeakLLMTaskExecutionFactory
from app.chat.context_input_provider import ChatContextInputProvider
from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.components import TaskComponents
from app.tasks.enums import TaskType
from app.prompts.prompt_provider import PromptProvider
from pathlib import Path
from app.tasks.enums import TaskExecutionStatus, TaskResultStatus
from app.artifacts.enums import ArtifactType, ArtifactOperation
from unittest.mock import AsyncMock
from app.application.tasks.task_results.stores.memory_store import InMemoryTaskResultStore

@pytest.mark.asyncio
async def test_execute_weak_llm_task():

    conversation_store = InMemoryConversationStore()
    task_store = InMemoryTaskStore()
    artifact_store = InMemoryArtifactStore()
    task_result_store = InMemoryTaskResultStore()
    prompt_provider = PromptProvider(Path("tests/prompts"))

    conversation = conversation_store.create()

    model_provider = AsyncMock(ModelProvider)
    model_provider.chat.return_value = OllamaModelOutput(
        content="Hallo!"
    )

    registry = TaskComponentRegistry()

    registry.register(TaskType.WEAK_LLM, TaskComponents(
        context_source_factory=OllamaChatContextSourceFactory(),
        context_builder=OllamaContextBuilder(prompt_provider),
        execution_factory=WeakLLMTaskExecutionFactory(artifact_store, model_provider),
        context_input_provider=ChatContextInputProvider(conversation_store)
    ))

    orchestrator = TaskOrchestrator(task_store, registry, task_result_store)

    task = task_store.create_task(
        TaskType.WEAK_LLM,
        conversation.id
    )

    execution = await orchestrator.execute(task)

    task_result = task_result_store.get_task_result(execution.id)
    assert task_result.error_code is None
    assert task_result.status == TaskResultStatus.SUCCESS

    assert execution.task_id == task.id
    assert execution.status == TaskExecutionStatus.COMPLETED

    model_provider.chat.assert_called_once()

    stored_task = task_store.get_task(task.id)
    stored_execution = task_store.get_task_execution(execution.id)

    assert stored_task is task
    assert stored_execution is execution

    artifacts = artifact_store.list_artifacts(execution.id)

    assert len(artifacts) == 1

    artifact = artifacts[0]

    assert artifact.task_execution_id == execution.id
    assert artifact.artifact_type == ArtifactType.LLM_RESPONSE
    assert artifact.operation == ArtifactOperation.CREATE
    assert artifact.data["content"] == "Hallo!"
