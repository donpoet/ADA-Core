from abc import ABC, abstractmethod
from app.conversation.models import Conversation, Message
from app.intent.models import Intent
from app.llm_models.provider import ModelProvider

class IntentRecognizer(ABC):

    @abstractmethod
    async def recognize(self, conversation: Conversation, message: Message) -> Intent:
        pass