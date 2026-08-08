from app.conversation.models import (
    Conversation,
    Message,
    MessageRole,
)


def test_conversation():
    conversation = Conversation()

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