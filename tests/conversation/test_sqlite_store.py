from sqlalchemy.orm import Session
from uuid import uuid4

from app.conversation.sqlite_store import SQLiteConversationStore
from app.database.schema import (
    ConversationModel,
    MessageModel
)
from app.conversation.models import (
    MessageRole,
    Conversation,
    Message
)
from datetime import (
    datetime,
    UTC,
)

def test_create_conversation(db_engine):
    store = SQLiteConversationStore(db_engine)

    conversation = store.create()

    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)

    conversation.created_at = created_at
    conversation.updated_at = updated_at

    assert conversation.id is not None
    assert conversation.created_at is not None
    assert conversation.updated_at is not None
    assert conversation.messages == []

    with Session(db_engine) as session:
        stored = session.get(
            ConversationModel,
            str(conversation.id),
        )

        assert stored is not None
        assert stored.id == str(conversation.id)
        assert stored.created_at is not None
        assert stored.updated_at is not None

def test_get_conversation(db_engine):
    conversation_id = uuid4()
    message_id = uuid4()

    with Session(db_engine) as session:
        conversation = ConversationModel(
            id=str(conversation_id),
        )

        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

        conversation.created_at = created_at
        conversation.updated_at = updated_at
        conversation.title = "Title"

        message = MessageModel(
            id=str(message_id),
            conversation_id=str(conversation_id),
            role=MessageRole.USER,
            content="Hallo Ada!",
        )

        conversation.messages.append(message)

        session.add(conversation)
        session.commit()
        assert session.get(
            ConversationModel,
            str(conversation_id),
        ) is not None

    store = SQLiteConversationStore(db_engine)

    result = store.get(conversation_id)

    assert isinstance(result, Conversation)
    assert result.id == conversation_id
    assert result.title == "Title"
    assert result.created_at == created_at
    assert result.updated_at == updated_at

    assert len(result.messages) == 1
    assert result.messages[0].id == message_id
    assert result.messages[0].role == MessageRole.USER
    assert result.messages[0].content == "Hallo Ada!"

def test_save_conversation(db_engine):
    created_at = datetime.now(UTC)
    updated_at = datetime.now(UTC)
    
    conversation = Conversation(
        created_at=created_at,
        updated_at=updated_at,
    )
    message1 = Message(
        role=MessageRole.USER,
        content="Hallo Ada!",
    )
    
    store = SQLiteConversationStore(db_engine)

    conversation.add_message(message1)

    conversation.title = "Title"
    conversation.created_at = created_at
    conversation.updated_at = updated_at
    store.save(conversation)

    with Session(db_engine) as session:
        result = session.get(
            ConversationModel,
            str(conversation.id),
        )

        assert result is not None
        assert result.id == str(conversation.id)
        assert result.title == "Title"
        assert result.created_at is not None
        assert result.updated_at is not None
        assert len(result.messages) == 1

        assert result.messages[0].id == str(message1.id)
        assert result.messages[0].role == message1.role
        assert result.messages[0].content == message1.content

    message2 = Message(
        role=MessageRole.ASSISTANT,
        content="Hallo! Wie kann ich dir helfen?"
    )
    conversation.add_message(message2)

    store.save(conversation)

    with Session(db_engine) as session:
        result = session.get(
            ConversationModel,
            str(conversation.id),
        )

        assert result is not None
        assert result.id == str(conversation.id)
        assert result.title == "Title"
        assert len(result.messages) == 2

        assert result.messages[0].id == str(message1.id)
        assert result.messages[0].role == message1.role
        assert result.messages[0].content == message1.content

        assert result.messages[1].id == str(message2.id)
        assert result.messages[1].role == message2.role
        assert result.messages[1].content == message2.content


def test_list_conversations(db_engine):
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

    store = SQLiteConversationStore(db_engine)

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

