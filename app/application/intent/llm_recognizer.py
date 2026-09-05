from app.conversation.models import Conversation, Message
from app.intent.models import Intent
from app.llm_models.provider import ModelProvider
from .recognizer import IntentRecognizer
from app.chat.context_source_factory import ChatContextSourceFactory
from app.context.context import ContextBuilder

class LLMIntentRecognizer(IntentRecognizer):
    def __init__(
        self,
        model_provider: ModelProvider, 
        context_source_factory: ChatContextSourceFactory,
        context_builder: ContextBuilder):
        self._model_provider = model_provider
        self._context_source_factory = context_source_factory
        self._context_builder = context_builder

    async def recognize(self, conversation: Conversation, message: Message) -> Intent:
        context_source = self._context_source_factory.create(conversation=conversation)
        context = self._context_builder.build(context_source)

        intent = await self._model_provider.structured(context, Intent)
        intent.source_message_id = message.id
        return intent