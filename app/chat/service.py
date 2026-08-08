from app.ollama.ollama_client import OllamaClient

class ChatService:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client

    async def chat(
            self, 
            model: str, 
            prompt: str
        ) -> str:
        return await self.ollama_client.generate(model=model, prompt=prompt) 