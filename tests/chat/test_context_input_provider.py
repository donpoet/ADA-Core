from app.tasks.models import Task
from app.tasks.enums import TaskType
from app.conversation.memory_store import InMemoryConversationStore
from app.chat.context_input_provider import ChatContextInputProvider

def test_get():
    conversation_store = InMemoryConversationStore()

    conversation = conversation_store.create()

    input_provider = ChatContextInputProvider(conversation_store)

    task = Task(
        conversation_id=conversation.id,
        type=TaskType.WEAK_LLM
    )

    result = input_provider.get(task)

    assert result is conversation
    assert result.id == conversation.id