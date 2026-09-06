from app.application.returns.return_decision_service import ReturnDecisionService
from app.returns.enums import ReturnAction
from app.events.models import TaskExecutionCompletedEvent
from app.context.context_source_factory import ContextSourceFactory
from app.context.context import ContextBuilder
from app.llm_models.provider import ModelProvider
from app.tasks.models import Task, TaskResult
from app.tasks.enums import TaskResultStatus, TaskStatus, TaskType
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.artifacts.models import Artifact
from app.conversation.models import Conversation, Message
from app.conversation.enums import MessageRole
from app.returns.models import ReturnContextSource
from unittest.mock import Mock, AsyncMock
from app.ollama.models import OllamaContextOutput
from uuid import uuid4
import pytest

@pytest.mark.asyncio
async def test_decide():
    conversation = Conversation()
    message = Message(
        role=MessageRole.USER,
        content="Schalte das Wohnzimmerlicht aus",
    )
    conversation.add_message(message)

    task_execution_id = uuid4()

    task = Task(
        conversation_id=conversation.id,
        type=TaskType.HOME_AUTOMATION,
    )

    task_result = TaskResult(
        task_execution_id=task_execution_id,
        status=TaskResultStatus.SUCCESS
    )

    artifacts = [
        Artifact(
           artifact_type=ArtifactType.HOME_ASSISTANT_AUTOMATION,
           operation=ArtifactOperation.CREATE,
           task_execution_id=task_execution_id,
           data={
                "device": "light:livingroom",
                "state": "on"
            }, 
        )
    ]

    context_source = ReturnContextSource(
        task=task,
        task_result=task_result,
        artifacts=artifacts,
        conversation=conversation,
    )

    context = OllamaContextOutput(
        messages=[
            {
                "role" : MessageRole.USER.value,
                "content": "test"
            }
        ]
    )

    context_source_factory = Mock(ContextSourceFactory)
    context_source_factory.create.return_value=context_source

    context_builder = Mock(ContextBuilder)
    context_builder.build.return_value=context

    model_provider = AsyncMock(ModelProvider)
    model_provider.structured.return_value=ReturnAction.RESPOND_NOW

    return_decision_service = ReturnDecisionService(
        context_source_factory=context_source_factory,
        context_builder=context_builder,
        model_provider=model_provider
    )

    event = TaskExecutionCompletedEvent(
        task_id=uuid4(),
        task_result_id=uuid4(),
        task_execution_id=uuid4())

    result = await return_decision_service.decide(event)

    assert result == ReturnAction.RESPOND_NOW

    context_source_factory.create.assert_called_once_with(event)
    context_builder.build.assert_called_once_with(context_source)
    model_provider.structured.assert_awaited_once_with(context, ReturnAction)



