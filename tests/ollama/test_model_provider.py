from app.ollama.model_provider import OllamaModelProvider
from app.ollama.models import OllamaChatResponse, OllamaMessage, OllamaContextOutput
from app.conversation.models import MessageRole

from unittest.mock import AsyncMock
import pytest

@pytest.mark.asyncio
async def test_chat():
    ollama_client = AsyncMock()

    ollama_client.chat.return_value = OllamaChatResponse(
        model="qwen3:4b",
        message=OllamaMessage(
            role=MessageRole.ASSISTANT.value,
            content="Hallo!"
        ),
        done=True,
    )

    ollama_model_provider = OllamaModelProvider(ollama_client, "qwen3:4b")

    result = await ollama_model_provider.chat(OllamaContextOutput(
        messages=[
            {
                "role":MessageRole.USER.value,
                "content":"Hallo Ada!"
            }
        ]
    ))

    assert result.content == "Hallo!"