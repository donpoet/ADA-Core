from app.chat.context_source_factory import ChatContextSourceFactory
from app.ollama.models import OllamaContextSource

class OllamaChatContextSourceFactory(ChatContextSourceFactory[OllamaContextSource]):

    def create(self, conversation: Conversation) -> OllamaContextSource:
        return OllamaContextSource(
            conversation=conversation
        )