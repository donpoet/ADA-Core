from app.ollama.model_provider import OllamaModelProvider
from app.ollama.models import OllamaChatResponse, OllamaMessage, OllamaContextOutput
from app.conversation.models import MessageRole

from unittest.mock import AsyncMock
import pytest

from pydantic import BaseModel

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

    ollama_model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})

    result = await ollama_model_provider.chat(OllamaContextOutput(
        messages=[
            {
                "role":MessageRole.USER.value,
                "content":"Hallo Ada!"
            }
        ]
    ))

    assert result.content == "Hallo!"

class TestType(BaseModel):
    field1: str
    field2: str

@pytest.mark.asyncio
async def test_structured():
    ollama_client = AsyncMock()

    ollama_client.structured.return_value = OllamaChatResponse(
        model="qwen3:4b",
        message=OllamaMessage(
            role=MessageRole.ASSISTANT.value,
            content='{"field1": "value1", "field2": "value2"}'
        ),
        done=True,
    )

    ollama_model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})

    result = await ollama_model_provider.structured(OllamaContextOutput(
        messages=[
            {
                "role":MessageRole.USER.value,
                "content":"classify"
            }
        ]
    ),
    TestType)

    assert isinstance(result, TestType)
    assert result.field1 == "value1"
    assert result.field2 == "value2"

@pytest.mark.asyncio
async def test_structured_with_parameters():
    ollama_client = AsyncMock()

    ollama_client.structured.return_value = OllamaChatResponse(
        model="qwen3:4b",
        message=OllamaMessage(
            role=MessageRole.ASSISTANT.value,
            content='{"field1": "value1", "field2": "value2"}'
        ),
        done=True,
    )

    ollama_model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})

    result = await ollama_model_provider.structured(OllamaContextOutput(
        messages=[
            {
                "role":MessageRole.USER.value,
                "content":"classify"
            }
        ]
    ),
    TestType
    )

    assert isinstance(result, TestType)
    assert result.field1 == "value1"
    assert result.field2 == "value2"

    assert ollama_client.structured.call_args[1]["thinking"] is False
    assert ollama_client.structured.call_args[1]["options"] == {"temperature": 0}
    
@pytest.mark.asyncio
async def test_chat_with_parameters():
    ollama_client = AsyncMock()

    ollama_client.chat.return_value = OllamaChatResponse(
        model="qwen3:4b",
        message=OllamaMessage(
            role=MessageRole.ASSISTANT.value,
            content="Hallo!"
        ),
        done=True,
    )

    ollama_model_provider = OllamaModelProvider(ollama_client, "qwen3:4b", thinking=False, options={"temperature": 0})

    result = await ollama_model_provider.chat(
        OllamaContextOutput(
            messages=[
                {
                    "role":MessageRole.USER.value,
                "content":"Hallo Ada!"
                }
            ]
        )
    )

    assert result.content == "Hallo!"

    assert ollama_client.chat.call_args[1]["thinking"] is False
    assert ollama_client.chat.call_args[1]["options"] == {"temperature": 0}