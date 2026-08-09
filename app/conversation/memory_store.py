from uuid import uuid4, UUID

from app.conversation.models import Conversation
from app.conversation.store import ConversationStore

class InMemoryConversationStore(ConversationStore):

    def __init__(self):
        self._conversations: dict[UUID, Conversation] = {}

    def create(self) -> Conversation:
        conversation = Conversation()
        self._conversations[conversation.id] = conversation
        return conversation

    def get(self, conversation_id: UUID) -> Conversation:
        return self._conversations.get(conversation_id)

    def save(self, conversation: Conversation) -> None:
        self._conversations[conversation.id] = conversation    