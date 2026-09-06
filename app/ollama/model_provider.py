from app.llm_models.provider import ModelProvider
from app.ollama.models import OllamaContextOutput, OllamaModelOutput
from app.ollama.ollama_client import OllamaClient
import json

class OllamaModelProvider(ModelProvider[OllamaContextOutput, OllamaModelOutput]):

    def __init__(self, ollama_client: OllamaClient, model: str, thinking: bool | None = None, options: dict | None = None):
        self.ollama_client = ollama_client
        self.model = model
        super().__init__(thinking=thinking, options=options)

    async def chat(self, input: OllamaContextOutput) -> OllamaModelOutput:
        response = await self.ollama_client.chat(self.model, input.messages, thinking=self.thinking, options=self.options)

        return OllamaModelOutput(
            content=response.message.content
        )

    async def structured(self, input: OllamaContextOutput, output_type: type[T]) -> T:
        response = await self.ollama_client.structured(model=self.model, messages=input.messages, output_type=output_type, thinking=self.thinking, options=self.options)

        data = json.loads(response.message.content)

        return output_type(**data)
