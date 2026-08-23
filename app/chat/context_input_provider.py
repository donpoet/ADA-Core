from app.context.context_input_provider import ContextInputProvider
from app.conversation.models import Conversation
from app.tasks.models import Task
from app.conversation.store import ConversationStore

class ChatContextInputProvider(ContextInputProvider[Conversation]):
    def __init__(self, conversation_store: ConversationStore):
        self._conversation_store = conversation_store
    
    def get(self, task: Task) -> Conversation:
        return self._conversation_store.get(task.conversation_id)