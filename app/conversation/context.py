from app.conversation.models import Conversation

class ContextBuilder:

    def build(self, conversation:Conversation) -> list[dict[str, str]]:
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in conversation.messages
        ]