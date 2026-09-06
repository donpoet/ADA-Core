from app.context.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    Message,
    MessageRole,
)
from app.chat.service import ChatService
import pytest
from unittest.mock import AsyncMock, Mock
from app.ollama.models import OllamaModelOutput
from app.ollama.context_builder import OllamaContextBuilder
from uuid import uuid4
from app.application.conversations.stores.memory_store import InMemoryConversationStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from pathlib import Path
from datetime import (
    datetime,
    UTC
)
from app.application.intent.recognizer import IntentRecognizer
from app.intent.models import Intent
from app.intent.enums import IntentAction
from app.application.tasks.task_factory import TaskFactory
from app.application.tasks.ochestrator import TaskOrchestrator
from app.tasks.enums import TaskType
from app.llm_models.provider import ModelProvider
import asyncio

class TestChatIntentRecognizer():
    def __init__(self, model_provider: ModelProvider):
        pass

    async def recognize(self, conversation: Conversation, message: Message):
        return Intent(
            intent_action=IntentAction.CHAT
        )


@pytest.mark.asyncio
async def test_chat_add_user_and_assistant_messages():
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    prompt_provider = PromptProvider(Path("tests/prompts"))
    context_builder = AsyncMock()
    conversation_store = InMemoryConversationStore()
    model_provider = AsyncMock()
    chat_context_source_factory = AsyncMock()
    intent_recognizer = TestChatIntentRecognizer(model_provider=model_provider)
    task_factory = Mock(TaskFactory)
    task_orchestrator = Mock(TaskOrchestrator)

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
        intent_recognizer=intent_recognizer,
        task_factory=task_factory,
        task_orchestrator=task_orchestrator,
        prompt_provider=prompt_provider,
    )

    conversation_store.save(conversation)

    result = await service.chat(
        conversation_id=conversation.id,
        message="Hallo Ada!",
    )

    assert result.content == "Hallo!"

    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[0].content == "Hallo Ada!"

    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[1].content == "Hallo!"

    model_provider.chat.assert_awaited_once()

@pytest.mark.asyncio
async def test_conversation_keeps_context():
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    
    prompt_provider = PromptProvider(Path("tests/prompts"))
    context_builder = AsyncMock()
    conversation_store = InMemoryConversationStore()
    model_provider = AsyncMock()
    chat_context_source_factory = AsyncMock()
    intent_recognizer = TestChatIntentRecognizer(model_provider=model_provider)
    task_factory = Mock(TaskFactory)
    task_orchestrator = Mock(TaskOrchestrator)

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
        intent_recognizer=intent_recognizer,
        task_factory=task_factory,
        task_orchestrator=task_orchestrator,
        prompt_provider=prompt_provider,
    )

    conversation_store.save(conversation)
        
    result = await service.chat(
        conversation_id=conversation.id,
        message="Hallo Ada!",
    )

    result = await service.chat(
        conversation_id=conversation.id,
        message="Hallo Ada!",
    )

    saved_conversation = conversation_store.get(conversation.id)
        
    assert len(saved_conversation.messages) == 4
    assert saved_conversation.messages[0].role == MessageRole.USER
    assert saved_conversation.messages[0].content == "Hallo Ada!"
        
    assert saved_conversation.messages[1].role == MessageRole.ASSISTANT
    assert saved_conversation.messages[1].content == "Hallo!"

    assert saved_conversation.messages[2].role == MessageRole.USER
    assert saved_conversation.messages[2].content == "Hallo Ada!"
                
    assert saved_conversation.messages[3].role == MessageRole.ASSISTANT
    assert saved_conversation.messages[3].content == "Hallo!"

@pytest.mark.asyncio
async def test_conversation_keeps_context_with_sqlite_store(db_engine):
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    prompt_provider = PromptProvider(Path("tests/prompts"))
    context_builder = AsyncMock()
    conversation_store = InMemoryConversationStore()
    model_provider = AsyncMock()
    chat_context_source_factory = AsyncMock()
    intent_recognizer = TestChatIntentRecognizer(model_provider=model_provider)
    task_factory = Mock(TaskFactory)
    task_orchestrator = Mock(TaskOrchestrator)

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
        intent_recognizer=intent_recognizer,
        task_factory=task_factory,
        task_orchestrator=task_orchestrator,
        prompt_provider=prompt_provider,
    )

    conversation_store.save(conversation)
        
    result = await service.chat(
        conversation_id=conversation.id,
        message="Hallo Ada!",
    )

    result = await service.chat(
        conversation_id=conversation.id,
        message="Hallo Ada!",
    )

    saved_conversation = conversation_store.get(conversation.id)
        
    assert len(saved_conversation.messages) == 4
    assert saved_conversation.messages[0].role == MessageRole.USER
    assert saved_conversation.messages[0].content == "Hallo Ada!"
        
    assert saved_conversation.messages[1].role == MessageRole.ASSISTANT
    assert saved_conversation.messages[1].content == "Hallo!"

    assert saved_conversation.messages[2].role == MessageRole.USER
    assert saved_conversation.messages[2].content == "Hallo Ada!"
                
    assert saved_conversation.messages[3].role == MessageRole.ASSISTANT
    assert saved_conversation.messages[3].content == "Hallo!"


@pytest.mark.asyncio
async def test_chat_creates_and_starts_task():
    conversation = Conversation()
    user_message = Message(
        role=MessageRole.USER,
        content="Fasse unseren Chat zusammen."
    )

    conversation_store = Mock()
    conversation_store.get.return_value = conversation

    prompt_provider = PromptProvider(Path("tests/prompts"))
    intent_recognizer = AsyncMock()
    intent_recognizer.recognize.return_value = Intent(
        intent_action=IntentAction.CREATE_TASK,
        task_type=TaskType.WEAK_LLM,
        source_message_id=user_message.id,
    )

    task = Mock()
    task.id = uuid4()

    task_factory = Mock()
    task_factory.create_task.return_value = task

    task_orchestrator = AsyncMock()

    model_provider = Mock()
    model_provider.chat = AsyncMock(
        return_value=Mock(content="Alles klar, ich kümmere mich darum.")
    )

    context_source_factory = Mock()
    context_builder = Mock()

    service = ChatService(
        model_provider=model_provider,
        context_source_factory=context_source_factory,
        context_builder=context_builder,
        conversation_store=conversation_store,
        intent_recognizer=intent_recognizer,
        task_factory=task_factory,
        task_orchestrator=task_orchestrator,
        prompt_provider=prompt_provider,
    )

    response = await service.chat(
        message=user_message.content,
        conversation_id=conversation.id,
    )

    task_factory.create_task.assert_called_once_with(
        task_type=TaskType.WEAK_LLM,
        conversation_id=conversation.id,
        source_message_id=user_message.id,
    )

    task_orchestrator.execute.assert_called_once_with(task)

    assert response.content == "Alles klar, ich kümmere mich darum."

    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT

    assert all(message.role != MessageRole.SYSTEM
        for message in conversation.messages
    )

class BlockingTestTaskOrchestrator:
    def __init__(self):
        self.started = asyncio.Event()
        self.finish = asyncio.Event()

    async def execute(self, task):
        self.started.set()
        await self.finish.wait()

@pytest.mark.asyncio
async def test_chat_does_not_wait_for_task_execution():
    conversation = Conversation()

    conversation_store = Mock()
    conversation_store.get.return_value = conversation

    intent_recognizer = AsyncMock()
    intent_recognizer.recognize.return_value = Intent(
        intent_action=IntentAction.CREATE_TASK,
        task_type=TaskType.WEAK_LLM,
        source_message_id=uuid4(),
    )

    task = Mock()
    task.id = uuid4()

    task_factory = Mock()
    task_factory.create_task.return_value = task

    task_orchestrator = BlockingTestTaskOrchestrator()

    model_provider = Mock()
    model_provider.chat = AsyncMock(
        return_value=Mock(
            content="Alles klar, ich kümmere mich darum."
        )
    )

    context_source_factory = Mock()
    context_builder = Mock()
    prompt_provider = PromptProvider(Path("tests/prompts"))

    service = ChatService(
        model_provider=model_provider,
        context_source_factory=context_source_factory,
        context_builder=context_builder,
        conversation_store=conversation_store,
        intent_recognizer=intent_recognizer,
        task_factory=task_factory,
        task_orchestrator=task_orchestrator,
        prompt_provider=prompt_provider,
    )

    response_task = asyncio.create_task(
        service.chat(
            message="Fasse unseren Chat zusammen.",
            conversation_id=conversation.id,
        )
    )

    await task_orchestrator.started.wait()

    assert not task_orchestrator.finish.is_set()

    response = await response_task

    assert response.content == "Alles klar, ich kümmere mich darum."

    assert not task_orchestrator.finish.is_set()

    task_orchestrator.finish.set()