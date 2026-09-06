from app.conversation.models import Conversation, Message
from app.intent.models import Intent
from app.application.intent.llm__intent_context_builder import LLMIntentContextBuilder
from app.application.intent.llm_recognizer import LLMIntentRecognizer
from app.application.intent.llm_intent_context_source_factory import LLMIntentRecognizerContextSourceFactory
from app.ollama.model_provider import OllamaModelProvider
from app.ollama.ollama_client import OllamaClient
from app.conversation.enums import MessageRole
from app.ollama.models import OllamaContextSource, OllamaContextOutput
from app.intent.enums import IntentAction
from app.tasks.enums import TaskType
from app.prompts.prompt_provider import PromptProvider

from pathlib import Path
import pytest

@pytest.mark.asyncio
async def test_recognize_explicit_task_request():
    conversation = Conversation()

    message = Message(
        role=MessageRole.USER,
        content="Erstelle einen Task für Home Automation"
    )

    conversation.add_message(message)

    ollama_client = OllamaClient(
        base_url="http://ada:11434",
        timeout=None)
    model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})
    context_source_factory = LLMIntentRecognizerContextSourceFactory()
    prompt_provider = PromptProvider(Path("tests/prompts"))
    context_builder = LLMIntentContextBuilder(prompt_provider=prompt_provider)

    intent_recognizer = LLMIntentRecognizer(
        model_provider,
        context_source_factory,
        context_builder
    )

    result = await intent_recognizer.recognize(conversation, message)

    assert isinstance(result, Intent)
    assert result.intent_action == IntentAction.CREATE_TASK
    assert result.task_type == TaskType.HOME_AUTOMATION
    assert result.source_message_id == message.id

@pytest.mark.asyncio
async def test_recognize_implicit_task_request():
    conversation = Conversation()

    message = Message(
        role=MessageRole.USER,
        content="Schalte das Wohnzimmerlicht ein"
    )

    conversation.add_message(message)

    ollama_client = OllamaClient(
        base_url="http://ada:11434",
        timeout=None)
    model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})
    context_source_factory = LLMIntentRecognizerContextSourceFactory()
    prompt_provider = PromptProvider(Path("tests/prompts"))
    context_builder = LLMIntentContextBuilder(prompt_provider=prompt_provider)

    intent_recognizer = LLMIntentRecognizer(
        model_provider,
        context_source_factory,
        context_builder
    )

    result = await intent_recognizer.recognize(conversation, message)

    assert isinstance(result, Intent)
    assert result.intent_action == IntentAction.CREATE_TASK
    assert result.task_type == TaskType.HOME_AUTOMATION
    assert result.source_message_id == message.id
