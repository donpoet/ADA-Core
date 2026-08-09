import pytest
from app.ollama.ollama_client import OllamaClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat():
    client = OllamaClient(
        base_url="http://ada:11434",
        timeout=None
    )

    response = await client.chat(
        model="qwen3:4b",
        messages= [
            {
                "role": "user",
                "content": "Antworte nur mit: Integrationstest erfolgreich."
            }
        ]
    )

    assert response.done is True
    assert response.message.role == "assistant"
    assert response.message.content