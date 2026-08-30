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

import pytest


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
        role=MessageRole.USER,
        content="Hallo Ada!"
    )

    conversation.add_message(message=message)

    assert len(conversation.messages) == 1
    assert conversation.messages[0] == message

def test_remove_message():
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

    message = Message(
            role=MessageRole.SYSTEM,
            content="instruction"
        )

    conversation.messages.append(message)

    assert len(conversation.messages) == 3
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[2].role == MessageRole.SYSTEM

    conversation.remove_system_message(message)

    assert len(conversation.messages) == 2
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT

def test_remove_message_non_system_message():
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

    message = Message(
            role=MessageRole.USER,
            content="Fass mir den text zusammen!"
        )

    conversation.messages.append(message)

    assert len(conversation.messages) == 3
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[2].role == MessageRole.USER

    with pytest.raises(ValueError):
        conversation.remove_system_message(message)

    assert len(conversation.messages) == 3
    assert conversation.messages[0].role == MessageRole.USER
    assert conversation.messages[1].role == MessageRole.ASSISTANT
    assert conversation.messages[2].role == MessageRole.USER