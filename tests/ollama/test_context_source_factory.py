from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.conversation.models import Conversation, Message, MessageRole

def test_create():
    conversation = Conversation()

    conversation.add_message(
        Message(
            role=MessageRole.USER,
            content="Hallo Ada!",
        )
    )

    conversation.add_message(
        Message(
            role=MessageRole.ASSISTANT,
            content="Hallo!",
        )
    )

    context_source_facotry = OllamaChatContextSourceFactory()

    result = context_source_facotry.create(conversation)

    assert len(result.conversation.messages) == 2
    assert result.conversation.id == conversation.id
    assert result.conversation.created_at == conversation.created_at
    assert result.conversation.updated_at == conversation.updated_at
    
    assert result.conversation.messages[0].role == MessageRole.USER
    assert result.conversation.messages[0].content == "Hallo Ada!"

    assert result.conversation.messages[1].role == MessageRole.ASSISTANT
    assert result.conversation.messages[1].content == "Hallo!"