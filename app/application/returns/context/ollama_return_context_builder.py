from app.context.context import ContextBuilder
from app.prompts.prompt_provider import PromptProvider
from app.returns.models import ReturnContextSource
from app.ollama.models import OllamaContextOutput
from app.returns.enums import ReturnAction
from app.prompts.prompt_provider import PromptProvider
from app.conversation.enums import MessageRole

class OllamaReturnContextBuilder(ContextBuilder[ReturnContextSource, OllamaContextOutput]):

    def __init__(self, prompt_provider):
        self._prompt_provider = prompt_provider

    def build(self, context_source: ReturnContextSource) -> OllamaContextOutput:
        task = context_source.task
        task_result = context_source.task_result
        artifacts = context_source.artifacts
        conversation = context_source.conversation

        return_actions = "\n".join(
            f"- {action.value}"
            for action in ReturnAction
        )

        conversation_messages = "\n".join(
            f"- {message.role}: {message.content}"
            for message in conversation.messages
        )

        prompt_artifacts = "\n\n".join(
            f"""ARTIFACT: 
            Type: {artifact.artifact_type.value} 
            Operation: {artifact.operation.value}
            Reference: {artifact.reference}
            Data: {artifact.data}"""
            for artifact in artifacts
        )

        prompt =  self._prompt_provider.get("return_decision")
        prompt = prompt.format(
            return_actions=return_actions,
            conversation_messages=conversation_messages,
            task_type=task.type.value,
            task_status=task.status.value,
            task_result_status=task_result.status.value,
            artifacts=prompt_artifacts
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