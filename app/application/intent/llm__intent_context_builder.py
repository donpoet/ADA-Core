from app.context.context import ContextBuilder
from app.prompts.prompt_provider import PromptProvider
from app.ollama.models import OllamaContextOutput
from app.intent.models import IntentContextSource
from app.conversation.models import MessageRole

class LLMIntentContextBuilder(ContextBuilder[IntentContextSource, OllamaContextOutput]):
    def __init__(self, prompt_provider):
        self.prompt_provider = prompt_provider


    def build(self, context_source: IntentContextSource) -> OllamaContextOutput:
            conversation = context_source.conversation

            intent_actions = "\n".join(
                f"- {action.value}"
                for action in context_source.intent_actions
            )

            task_types = "\n".join(
                f"- {task_type.value}: {task_type.description}"
                for task_type in context_source.task_types
            )

            conversation_messages = "\n".join(
                f"- {message.role}: {message.content}"
                for message in conversation.messages
            )

            prompt =  self.prompt_provider.get("intent_recognition")
            prompt = prompt.format(
                intent_actions=intent_actions,
                task_types=task_types,
                conversation_messages=conversation_messages,
            )

            messages = []
            messages.append(
                {
                    "role": MessageRole.SYSTEM.value,
                    "content": prompt
                }
            )

            return OllamaContextOutput(
                messages=messages
            )