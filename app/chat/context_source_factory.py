from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.context.context_source_factory import ContextSourceFactory
from app.conversation.models import Conversation

S = TypeVar("S")

class ChatContextSourceFactory(ContextSourceFactory[Conversation, S]):
    
    def create(self, conversation: Conversation) -> S:
        pass