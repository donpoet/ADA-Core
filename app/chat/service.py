from app.ollama.ollama_client import OllamaClient
from app.conversation.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    MessageRole,
    Message,
)

class ChatService:
    def __init__(
            self, 
            ollama_client: OllamaClient,
            context_builder: ContextBuilder):
        self.ollama_client = ollama_client
        self.context_builder = context_builder

    async def chat(
            self, 
            converstaion: Conversation, 
            message: str
        ) -> str:

        converstaion.add_message(
            Message(
                role=MessageRole.USER,
                content=message,
            )
        )

        context = self.context_builder.build(converstaion)

        response = await self.ollama_client.chat(
            model="qwen3:4b", # Later changed by model selector
            messages=context,
        )

        converstaion.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content=response.message.content,
            )
        )

        return response.message.content