from app.context.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    MessageRole,
)
from app.chat.service import ChatService
import pytest
from unittest.mock import AsyncMock
from app.ollama.models import OllamaModelOutput
from app.ollama.context_builder import OllamaContextBuilder
from app.ollama.model_provider import OllamaModelProvider
from uuid import uuid4
from app.conversation.memory_store import InMemoryConversationStore
from app.conversation.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from pathlib import Path
from datetime import (
    datetime,
    UTC
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

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
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

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
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

    model_provider.chat.return_value = OllamaModelOutput(
       content="Hallo!"
    )

    service = ChatService(
        context_source_factory=chat_context_source_factory,
        model_provider=model_provider,
        context_builder=context_builder,
        conversation_store=conversation_store,
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