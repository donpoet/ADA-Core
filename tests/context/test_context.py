from app.context.context import ContextBuilder
from app.conversation.models import(
    Conversation,
    Message,
    MessageRole
)
from pathlib import Path
from app.prompts.prompt_provider import PromptProvider
from uuid import uuid4
from datetime import (
    datetime,
    UTC
)

def test_add_system_prompt():
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    prompt_provider = PromptProvider(Path("tests/prompts"))
    builder = ContextBuilder(prompt_provider)
    context = builder.build(conversation=conversation)

    assert context == [
        {
            "role": "system",
            "content": "test"
        }
    ]

def test_build_context():
    conversation = Conversation(
        id=uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

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

    prompt_provider = PromptProvider(Path("tests/prompts"))
    builder = ContextBuilder(prompt_provider)
    context = builder.build(conversation=conversation)

    assert context == [
        {
            "role": "system",
            "content": "test"
        },
        {
            "role": "user",
            "content": "Hallo Ada!"
        },
        {
            "role": "assistant",
            "content": "Hallo! Wie kann ich dir helfen?"
        },
    ]
