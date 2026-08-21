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
from app.llm_models.provider import ModelProvider
from app.chat.context_source_factory import ChatContextSourceFactory

class ChatService:
    def __init__(
            self, 
            model_provider: ModelProvider,
            context_source_factory: ChatContextSourceFactory,
            context_builder: ContextBuilder,
            conversation_store: ConversationStore):
        self.model_provider = model_provider
        self.context_source_factory = context_source_factory
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

        source = self.context_source_factory.create(conversation)

        context = self.context_builder.build(source)

        output = await self.model_provider.chat(context)

        conversation.add_message(
            Message(
                role=MessageRole.ASSISTANT,
                content=output.content,
            )
        )

        self.conversation_store.save(conversation)

        return ChatServiceResponse(
            conversation_id=conversation.id,
            content=output.content,
        )