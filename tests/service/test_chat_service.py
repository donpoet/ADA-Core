from app.conversation.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    MessageRole,
    Message,
)
from app.chat.service import ChatService
import pytest
from unittest.mock import AsyncMock
from app.ollama.models import OllamaChatResponse

@pytest.mark.asyncio
async def test_chat_add_user_and_assistant_messages():
    conversation = Conversation()
    ollama_client = AsyncMock()

    ollama_client.chat.return_value = OllamaChatResponse(
        model="qwen3:4b",
        message={
            "role": "assistant",
            "content": "Hallo!",
        },
        done=True
    )

    context_builder = ContextBuilder()

    service = ChatService(
        ollama_client=ollama_client,
        context_builder=context_builder,
    )

    result = await service.chat(
        converstaion=conversation,
        message="Hallo Ada!",
    )

    assert result == "Hallo!"

    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[0].content == "Hallo Ada!"

    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[1].content == "Hallo!"

    ollama_client.chat.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_conversation_keeps_context():
        conversation = Conversation()
        ollama_client = AsyncMock()
        
        ollama_client.chat.return_value = OllamaChatResponse(
            model="qwen3:4b",
            message={
                "role": "assistant",
                "content": "Hallo!",
            },
            done=True
        )
        
        context_builder = ContextBuilder()
        
        service = ChatService(
            ollama_client=ollama_client,
            context_builder=context_builder,
        )
        
        result = await service.chat(
            converstaion=conversation,
            message="Hallo Ada!",
        )

        result = await service.chat(
                    converstaion=conversation,
                    message="Hallo Ada!",
                )
        
        assert len(conversation.messages) == 4
        assert conversation.messages[0].role == MessageRole.USER
        assert conversation.messages[0].content == "Hallo Ada!"
        
        assert conversation.messages[1].role == MessageRole.ASSISTANT
        assert conversation.messages[1].content == "Hallo!"

        assert conversation.messages[2].role == MessageRole.USER
        assert conversation.messages[2].content == "Hallo Ada!"
                
        assert conversation.messages[3].role == MessageRole.ASSISTANT
        assert conversation.messages[3].content == "Hallo!"
        