from app.ollama.ollama_client import OllamaClient
from app.context.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    MessageRole,
    Message,
)
from app.conversation.memory_store import ConversationStore
from uuid import UUID
from app.chat.models import ChatServiceResponse

class ChatService:
    def __init__(
            self, 
            ollama_client: OllamaClient,
            context_builder: ContextBuilder,
            conversation_store: ConversationStore ):
        self.ollama_client = ollama_client
        self.context_builder = context_builder
        self.conversation_store = conversation_store

    async def chat(
            self, 
            message: str,
            conversation_id: UUID | None = None, 
        ) -> ChatServiceResponse:

        conversation = None
        
        if conversation_id is not None:
            conversation = self.conversation_store.get(conversation_id)
        
        if conversation is None:
            conversation = self.conversation_store.create()

        conversation.add_message(
            Message(
                role=MessageRole.USER,
                content=message,
            )
        )

        context = self.context_builder.build(conversation)

        response = await self.ollama_client.chat(
            model="qwen3:4b", # Later changed by model selector
            messages=context,
        )

        conversation.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content=response.message.content,
            )
        )

        self.conversation_store.save(conversation)

        return ChatServiceResponse(
            conversation_id=conversation.id,
            content=response.message.content,
        )