from app.application.returns.context.ollama_return_context_builder import OllamaReturnContextBuilder
from app.returns.models import ReturnContextSource
from app.returns.enums import ReturnAction
from app.tasks.models import Task, TaskResult
from app.tasks.enums import TaskResultStatus, TaskStatus, TaskType
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.artifacts.models import Artifact
from app.conversation.models import Conversation, Message
from app.conversation.enums import MessageRole
from app.ollama.models import OllamaContextOutput

from app.prompts.prompt_provider import PromptProvider

from uuid import uuid4
from pathlib import Path

def test_build():
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

    prompt_provider = PromptProvider(Path("tests/prompts"))

    context_builder = OllamaReturnContextBuilder(prompt_provider)

    result = context_builder.build(context_source)

    assert isinstance(result, OllamaContextOutput)
    assert result.messages[0]["role"] == MessageRole.SYSTEM.value

    message = result.messages[0]["content"]

    assert "Schalte das Wohnzimmerlicht aus" in message
    assert task.type.value in message
    assert task_result.status.value in message
    assert task.status.value in message
    assert artifacts[0].artifact_type.value in message
    assert artifacts[0].operation.value in message
    assert str(artifacts[0].data) in message

