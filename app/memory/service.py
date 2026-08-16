from app.conversation.store import ConversationStore
from app.conversation.models import Conversation
from uuid import UUID

class MemoryService():
    def __init__(self, store: ConversationStore):
        self._store = store

    def list_conversations(self) -> list[Conversation]:
        conversations = self._store.list_conversations()
        
        return sorted(
            conversations,
            key=lambda conversation: conversation.updated_at,
            reverse=True,
        ) 

    def get_conversation(self, conversation_id:UUID) :
        return self._store.get(conversation_id)

