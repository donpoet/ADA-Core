from app.application.intent.llm__intent_context_builder import LLMIntentContextBuilder
from app.conversation.models import Conversation, Message, MessageRole
from app.intent.enums import IntentAction
from app.tasks.enums import TaskType
from app.ollama.models import OllamaContextOutput
from app.intent.models import IntentContextSource
from app.prompts.prompt_provider import PromptProvider
from pathlib import Path

def test_build():
    prompt_provider = PromptProvider(Path("tests/prompts"))
    conversation = Conversation()
    context_builder = LLMIntentContextBuilder(prompt_provider=prompt_provider)
    context_source = IntentContextSource(
        conversation=conversation,
        task_types=[TaskType.WEAK_LLM],
        intent_actions=[IntentAction.CREATE_TASK]
    )
    context_source.conversation.add_message(
        Message(role=MessageRole.USER, content="Erstelle einen Task")
    )

    result = context_builder.build(context_source)

    assert isinstance(result, OllamaContextOutput)
    assert len(result.messages) == 1
    assert result.messages[0]["role"] == MessageRole.SYSTEM.value
    assert "Erstelle einen Task" in result.messages[0]["content"]
    assert "- create_task" in result.messages[0]["content"]
    assert "- weak_llm:" in result.messages[0]["content"]