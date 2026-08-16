from sqlalchemy.orm import Session
from uuid import uuid4

from app.database.database import Base
from app.database.schema import (
    ConversationModel,
    MessageModel
)
from app.conversation.models import MessageRole

def test_conversation_can_be_persisted(db_engine):
    conversation_id = uuid4()

    conversation = ConversationModel(
        id=str(conversation_id),
    )

    user_message_id = str(uuid4())
    user_message = MessageModel(
        id=user_message_id,
        role=MessageRole.USER,
        content="Hallo Ada!",
    )

    assistent_message_id = str(uuid4())
    assistent_message = MessageModel(
        id=assistent_message_id,
        role=MessageRole.ASSISTANT,
        content="Hallo! Wie kann ich dir helfen?",
    )

    conversation.messages.append(user_message)
    conversation.messages.append(assistent_message)

    with Session(db_engine) as session:
        session.add(conversation)
        session.commit()

    with Session(db_engine) as session:
        loaded_conversation = session.get(
            ConversationModel,
            str(conversation_id),
        )

        assert loaded_conversation is not None

        assert loaded_conversation.id == str(conversation_id)
        assert len(loaded_conversation.messages) == 2

        loaded_user_message = loaded_conversation.messages[0]
        loaded_assistant_message = loaded_conversation.messages[1]

        assert loaded_user_message.id == user_message_id
        assert loaded_user_message.role == MessageRole.USER
        assert loaded_user_message.content == "Hallo Ada!"

        assert loaded_assistant_message.id == assistent_message_id
        assert loaded_assistant_message.role == MessageRole.ASSISTANT
        assert loaded_assistant_message.content == "Hallo! Wie kann ich dir helfen?"

def test_conversations_can_be_deleted_without_orphaned_messages(db_engine):
    conversation_id = str(uuid4())

    conversation = ConversationModel(
        id=conversation_id,
    )

    user_message_id = str(uuid4())
    user_message = MessageModel(
        id=user_message_id,
        role=MessageRole.USER,
        content="Hallo Ada!",
    )

    assistent_message_id = str(uuid4())
    assistent_message = MessageModel(
        id=assistent_message_id,
        role=MessageRole.ASSISTANT,
        content="Hallo! Wie kann ich dir helfen?",
    )

    conversation.messages.append(user_message)
    conversation.messages.append(assistent_message)

    with Session(db_engine) as session:
        session.add(conversation)
        session.commit()
    
    with Session(db_engine) as session:
        loaded_conversation = session.get(
            ConversationModel,
            str(conversation_id),
        )

        assert loaded_conversation is not None

        assert loaded_conversation.id == str(conversation_id)
        assert len(loaded_conversation.messages) == 2

        session.delete(loaded_conversation)
        session.commit()

        assert session.get(
            ConversationModel, 
            conversation_id,
        ) is None

        assert session.get(
            MessageModel,
            user_message_id
        ) is None

        assert session.get(
            MessageModel,
            assistent_message_id
        ) is None