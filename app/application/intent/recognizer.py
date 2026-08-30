from abc import ABC, abstractmethod
from app.conversation.models import Conversation, Message
from app.intent.models import Intent
from app.llm_models.provider import ModelProvider

class IntentRecognizer(ABC):
    def __init__(self, model_provider: ModelProvider):
        self._model_provider = model_provider

    @abstractmethod
    async def recognize(self, conversation: Conversation, message: Message) -> Intent:
        pass