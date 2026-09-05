from app.chat.context_source_factory import ChatContextSourceFactory
from app.intent.models import IntentContextSource

from app.tasks.enums import TaskType
from app.intent.enums import IntentAction

class LLMIntentRecognizerContextSourceFactory(ChatContextSourceFactory[IntentContextSource]):
    def create(self, conversation: Conversation) -> IntentContextSource:
        return IntentContextSource(
            conversation=conversation,
            task_types=list(TaskType),
            intent_actions=list(IntentAction),
        )
