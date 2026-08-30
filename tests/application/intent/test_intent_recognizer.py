from app.application.intent.recognizer import IntentRecognizer
from app.intent.models import Intent
from app.intent.enums import IntentAction
from app.conversation.models import Conversation, Message
from app.conversation.enums import MessageRole
from app.tasks.enums import TaskType
from app.llm_models.provider import ModelProvider

from unittest.mock import Mock
import pytest

class TestIntentRecognizer(IntentRecognizer):
    async def recognize(self, conversation: Conversation, message: Message) -> Intent:
        return Intent(
            intent_action=IntentAction.CREATE_TASK,
            task_type=TaskType.WEAK_LLM,
            source_message_id=message.id
        )

@pytest.mark.asyncio
async def test_recognize():
    conversation = Conversation()
    message = Message(
        role=MessageRole.USER,
        content="Fasse unseren Chat zusammen."
    )
    conversation.add_message(message)

    model_provider = Mock(ModelProvider)

    intent_recognizer=TestIntentRecognizer(
        model_provider=model_provider
    )

    intent = await intent_recognizer.recognize(conversation, message)

    assert intent.intent_action == IntentAction.CREATE_TASK
    assert intent.task_type == TaskType.WEAK_LLM
    assert intent.source_message_id == message.id