from app.conversation.memory_store import InMemoryConversationStore
from app.conversation.models import (
    Message,
    MessageRole
)
from uuid import uuid4

def test_create_and_get_conversation():
    store = InMemoryConversationStore()

    conversation = store.create()

    result = store.get(conversation.id)

    assert result is conversation

def test_save_conversation():
    store = InMemoryConversationStore()

    conversation = store.create()
    conversation.add_message(
        message= Message(
            role= MessageRole.USER,
            content= "Hallo Ada!"
        ) 
    )

    store.save(conversation)

    result = store.get(conversation_id=conversation.id)

    assert result is conversation
    assert len(result.messages) == 1

def test_get_unknown_conversation_returns_none():
    store = InMemoryConversationStore()

    result = store.get(uuid4())

    assert result is None