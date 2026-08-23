from app.artifacts.models import Artifact
from app.application.tasks.executions.weak_llm.execution import WeakLLMTaskExecution
from app.ollama.models import OllamaContextOutput
from app.conversation.models import MessageRole
from app.application.artifacts.stores.artifact_store import ArtifactStore
from app.llm_models.provider import ModelProvider
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.tasks.enums import TaskResultStatus
from app.ollama.models import OllamaModelOutput

from uuid import uuid4, UUID
from unittest.mock import AsyncMock

import pytest

@pytest.mark.asyncio
async def test_successful_execution():

    task_exection_id = uuid4()

    artifact_store = AsyncMock(ArtifactStore)
    artifact_store.create_artifact.return_value = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        reference=None,
        task_execution_id=task_exection_id,
        data={
            "content" : "Hallo!"
        }
    )

    model_provider = AsyncMock(ModelProvider)
    model_provider.chat.return_value = OllamaModelOutput(
        content="Hallo!"
    )

    execution = WeakLLMTaskExecution(
        task_exection_id,
        OllamaContextOutput(
            messages=[
                {
                    "role": MessageRole.USER,
                    "content": "Hallo Ada!"
                },
            ]
        ),
        artifact_store,
        model_provider
    )

    result = await execution.execute()

    artifact_store.create_artifact.assert_called_once()
    model_provider.chat.assert_called_once()

    assert result.error_code is None
    assert result.status is TaskResultStatus.SUCCESS

@pytest.mark.asyncio
async def test_failed_execution_when_model_provider_fais():

    task_exection_id = uuid4()

    artifact_store = AsyncMock(ArtifactStore)
    artifact_store.create_artifact.return_value = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        reference=None,
        task_execution_id=task_exection_id,
        data={
            "content" : "Hallo!"
        }
    )

    model_provider = AsyncMock(ModelProvider)
    model_provider.chat.side_effect = RuntimeError("LLM unavailable")

    execution = WeakLLMTaskExecution(
        task_exection_id,
        OllamaContextOutput(
            messages=[
                {
                    "role": MessageRole.USER,
                    "content": "Hallo Ada!"
                },
            ]
        ),
        artifact_store,
        model_provider
    )

    result = await execution.execute()

    artifact_store.create_artifact.assert_not_called()
    model_provider.chat.assert_called_once()

    assert result.error_code is not None
    assert result.status is TaskResultStatus.FAILED

@pytest.mark.asyncio
async def test_failed_execution_when_artifact_creation_fails():

    task_exection_id = uuid4()

    artifact_store = AsyncMock(ArtifactStore)
    artifact_store.create_artifact.side_effect = RuntimeError("Artifact Storage unavailable")

    model_provider = AsyncMock(ModelProvider)
    model_provider.chat.return_value = OllamaModelOutput(
        content="Hallo!"
    )

    execution = WeakLLMTaskExecution(
        task_exection_id,
        OllamaContextOutput(
            messages=[
                {
                    "role": MessageRole.USER,
                    "content": "Hallo Ada!"
                },
            ]
        ),
        artifact_store,
        model_provider
    )

    result = await execution.execute()

    artifact_store.create_artifact.assert_called_once()
    model_provider.chat.assert_called_once()

    assert result.error_code is not None
    assert result.status is TaskResultStatus.FAILED