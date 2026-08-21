from app.llm_models.provider import ModelProvider
from app.ollama.models import OllamaContextOutput, OllamaModelOutput
from app.ollama.ollama_client import OllamaClient

class OllamaModelProvider(ModelProvider[OllamaContextOutput, OllamaModelOutput]):

    def __init__(self, ollama_client: OllamaClient, model: str):
        self.ollama_client = ollama_client
        self.model = model
    
    async def chat(self, input: OllamaContextOutput) -> OllamaModelOutput:
        response = await self.ollama_client.chat(self.model, input.messages)

        return OllamaModelOutput(
            content=response.message.content
        )


