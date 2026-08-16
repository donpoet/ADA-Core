from app.conversation.store import ConversationStore
from app.conversation.models import Conversation

class MemoryService():
    def __init__(self, store: ConversationStore):
        self._store = store

    def list_conversations(self) -> list[Conversation]:
        return self._store.list_conversations()    