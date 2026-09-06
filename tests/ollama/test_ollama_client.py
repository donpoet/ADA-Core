import pytest
from app.ollama.ollama_client import OllamaClient
from pydantic import BaseModel

class TestOutput(BaseModel):
    field1: str
    field2: str

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
        ],
        thinking=False,
        options={
            "temperature": 0,
        },
    )

    assert response.done is True
    assert response.message.role == "assistant"
    assert response.message.content

@pytest.mark.asyncio
async def test_structured():
    client = OllamaClient(
        base_url="http://ada:11434",
        timeout=None
    )

    response = await client.structured(
        model="qwen3:4b",
        messages= [
            {
                "role": "user",
                "content": "Antworte nur mit einem json Objekt mit den Feldern field1 und field2, wobei field1 den Wert 'value1' und field2 den Wert 'value2' hat."
            }
        ],
        output_type=TestOutput,
        thinking=False,
        options={
            "temperature": 0,
        },
    )

    assert response.done is True
    assert response.message.role == "assistant"

    result_object = TestOutput.parse_raw(response.message.content)
    assert isinstance(result_object, TestOutput)
    assert result_object.field1 == "value1"
    assert result_object.field2 == "value2"
   