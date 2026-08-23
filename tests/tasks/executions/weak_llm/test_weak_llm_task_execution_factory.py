from app.artifacts.models import Artifact
from app.application.tasks.executions.weak_llm.execution import WeakLLMTaskExecution
from app.application.tasks.executions.weak_llm.execution_factory import WeakLLMTaskExecutionFactory
from app.ollama.models import OllamaContextOutput
from app.conversation.models import MessageRole
from app.application.artifacts.stores.artifact_store import ArtifactStore
from app.llm_models.provider import ModelProvider
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.tasks.enums import TaskResultStatus
from app.ollama.models import OllamaModelOutput

from uuid import uuid4, UUID
from unittest.mock import AsyncMock

def test_create_execution():
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

    factory = WeakLLMTaskExecutionFactory(
        artifact_store,
        model_provider,
    )

    execution = factory.create(uuid4(), OllamaContextOutput(
        messages=[
                {
                    "role": MessageRole.USER,
                    "content": "Hallo Ada!"
                },
            ]
    ))

    assert isinstance(execution, WeakLLMTaskExecution)
    assert execution._artifact_store is artifact_store
    assert execution._model_provider is model_provider