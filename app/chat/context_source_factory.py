from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.conversation.models import Conversation

S = TypeVar("S")

class ChatContextSourceFactory(ABC, Generic[S]):
    
    @abstractmethod
    def create(self, conversation: Conversation) -> S:
        pass