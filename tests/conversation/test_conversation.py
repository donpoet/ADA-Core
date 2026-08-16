from app.conversation.models import (
    Conversation,
    Message,
    MessageRole,
)
from datetime import (
    datetime,
    UTC
)
from uuid import uuid4


def test_conversation():
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    conversation.messages.append(
        Message(
            role=MessageRole.USER,
            content="Hello Ada!",
        )
    )

    conversation.messages.append(
        Message(
            role=MessageRole.ASSISTANT,
            content="Hallo! Wie kann ich dir helfen?"
        )
    )
    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT

    def test_add_message():
        conversation = Conversation()

        message = Message(
            MessageRole.USER,
            "Hallo Ada!"
        )

        conversation.add_message(message=message)

        assert len(conversation.messages) == 1
        assert conversation.messages[0] == message