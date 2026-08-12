from app.conversation.models import (
    Conversation,
    MessageRole
) 
from app.prompts.prompt_provider import PromptProvider


class ContextBuilder:

    def __init__(self, prompt_provider):
        self.prompt_provider = prompt_provider

    def build(self, conversation:Conversation) -> list[dict[str, str]]:
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

        return messages