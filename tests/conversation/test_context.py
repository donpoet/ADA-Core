from app.conversation.context import ContextBuilder
from app.conversation.models import(
    Conversation,
    Message,
    MessageRole
)

def test_build_context():
    conversation = Conversation()

    conversation.add_message(
        Message(
            role= MessageRole.USER,
            content= "Hallo Ada!"
        )
    )

    conversation.add_message(
        Message(
            role= MessageRole.ASSISTANT,
            content= "Hallo! Wie kann ich dir helfen?"
        )
    )

    builder = ContextBuilder()
    context = builder.build(conversation=conversation)

    assert context == [
        {
            "role": "user",
            "content": "Hallo Ada!"
        },
        {
            "role": "assistant",
            "content": "Hallo! Wie kann ich dir helfen?"
        },
    ]
