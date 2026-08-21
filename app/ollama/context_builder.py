from app.context.context import ContextBuilder
from app.prompts.prompt_provider import PromptProvider
from app.ollama.models import OllamaContextSource, OllamaContextOutput
from app.conversation.models import MessageRole

class OllamaContextBuilder(ContextBuilder[OllamaContextSource, OllamaContextOutput]):
    def __init__(self, prompt_provider):
        self.prompt_provider = prompt_provider


    def build(self, context_source: OllamaContextSource) -> OllamaContextOutput:
            conversation = context_source.conversation
            messages = []
            messages.append(
                {
                    "role": MessageRole.SYSTEM.value,
                    "content": self.prompt_provider.get("system")
                }
            )

            for message in conversation.messages:
                messages.append(
                    {
                        "role": message.role.value,
                        "content": message.content
                    }
                )

            return OllamaContextOutput(
                messages=messages
            )