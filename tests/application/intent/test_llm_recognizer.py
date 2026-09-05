from app.conversation.models import Conversation, Message
from app.intent.models import Intent
from app.llm_models.provider import ModelProvider
from app.chat.context_source_factory import ChatContextSourceFactory
from app.context.context import ContextBuilder
from app.application.intent.llm_recognizer import LLMIntentRecognizer
from unittest.mock import Mock, AsyncMock
from app.conversation.enums import MessageRole
from app.ollama.models import OllamaContextSource, OllamaContextOutput
from app.intent.enums import IntentAction
from app.tasks.enums import TaskType

import pytest

@pytest.mark.asyncio
async def test_recognize():
    conversation = Conversation()

    message = Message(
        role=MessageRole.USER,
        content="Erstelle einen Task"
    )

    conversation.add_message(message)

    model_provider = AsyncMock(ModelProvider)
    model_provider.structured.return_value = Intent(
        intent_action=IntentAction.CREATE_TASK,
        task_type=TaskType.WEAK_LLM,
    )

    context_source_factory = Mock(ChatContextSourceFactory)
    context_source_factory.create.return_value=OllamaContextSource(
        conversation=conversation
    )

    context_builder = Mock(ContextBuilder)
    context_builder.build.return_value = OllamaContextOutput(
        messages=[{
            "role": MessageRole.USER.value,
            "content": "Erstelle einen Task"
        }]
    )

    intent_recognizer = LLMIntentRecognizer(
        model_provider,
        context_source_factory,
        context_builder
    )

    result = await intent_recognizer.recognize(conversation, message)

    assert isinstance(result, Intent)
    assert result.intent_action == IntentAction.CREATE_TASK
    assert result.task_type == TaskType.WEAK_LLM
    assert result.source_message_id == message.id

    model_provider.structured.assert_called_once()
    context_source_factory.create.assert_called_once()
    context_builder.build.assert_called_once()
