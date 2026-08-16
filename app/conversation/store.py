from abc import ABC, abstractmethod
from app.conversation.models import Conversation
from uuid import UUID

class ConversationStore(ABC):

    @abstractmethod
    def create(self) -> Conversation:
        pass

    @abstractmethod
    def get(self, conversation_id: UUID) -> Conversation:
        pass

    @abstractmethod
    def save(self, conversation:Conversation) -> None:
        pass

    @abstractmethod
    def list_conversations(self) -> list[Conversation]:
        pass