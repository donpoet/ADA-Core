from app.conversation.memory_store import InMemoryConversationStore
from app.conversation.models import (
    Conversation,
    Message,
    MessageRole
)
from uuid import uuid4
from datetime import (
    datetime,
    UTC
)

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

def test_list_conversations():
    conversation1 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conversation2 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conversation3 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    store = InMemoryConversationStore()

    store.save(conversation1)
    store.save(conversation2)
    store.save(conversation3)

    result = store.list_conversations()

    assert len(result) == 3

    resutl_ids = {conversation.id for conversation in result}

    assert resutl_ids == {
        conversation1.id,
        conversation2.id,
        conversation3.id
    }
    