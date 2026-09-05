from app.application.intent.llm_intent_context_source_factory import LLMIntentRecognizerContextSourceFactory
from app.tasks.enums import TaskType
from app.intent.enums import IntentAction
from app.conversation.models import Conversation

def test_create():
    conversation = Conversation()
    factory = LLMIntentRecognizerContextSourceFactory()
    context_source = factory.create(conversation)

    assert context_source.conversation == conversation
    assert set(context_source.task_types) == set(TaskType)
    assert set(context_source.intent_actions) == set(IntentAction)