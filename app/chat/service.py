from app.ollama.ollama_client import OllamaClient
from app.context.context import ContextBuilder
from app.conversation.models import (
    Conversation,
    MessageRole,
    Message,
)
from app.application.conversations.stores.memory_store import ConversationStore
from uuid import UUID
from app.chat.models import ChatServiceResponse
from app.llm_models.provider import ModelProvider
from app.chat.context_source_factory import ChatContextSourceFactory
from app.application.intent.recognizer import IntentRecognizer
from app.intent.enums import IntentAction
from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.task_factory import TaskFactory
from app.prompts.prompt_provider import PromptProvider

import asyncio

class ChatService:
    def __init__(
            self, 
            model_provider: ModelProvider,
            context_source_factory: ChatContextSourceFactory,
            context_builder: ContextBuilder,
            conversation_store: ConversationStore,
            intent_recognizer: IntentRecognizer,
            task_factory: TaskFactory,
            task_orchestrator: TaskOrchestrator,
            prompt_provider: PromptProvider):
        self.model_provider = model_provider
        self.context_source_factory = context_source_factory
        self.context_builder = context_builder
        self.conversation_store = conversation_store
        self.intent_recognizer = intent_recognizer
        self.task_factory = task_factory
        self.task_orchestrator = task_orchestrator
        self.prompt_provider = prompt_provider

    async def chat(
            self, 
            message: str,
            conversation_id: UUID | None = None, 
        ) -> ChatServiceResponse:

        conversation = None
        
        if conversation_id is not None:
            conversation = self.conversation_store.get(conversation_id)
        
        if conversation is None:
            conversation = self.conversation_store.create()

        user_message = Message(
                role=MessageRole.USER,
                content=message,
            )

        conversation.add_message(user_message)

        intent = await self.intent_recognizer.recognize(conversation=conversation, message=user_message)

        if intent.intent_action == IntentAction.CHAT:       

            source = self.context_source_factory.create(conversation)

            context = self.context_builder.build(source)

            output = await self.model_provider.chat(context)

            conversation.add_message(
                Message(
                    role=MessageRole.ASSISTANT,
                    content=output.content,
                )
            )
        else:

            task = self.task_factory.create_task(
                task_type=intent.task_type,
                conversation_id=conversation.id,
                source_message_id=intent.source_message_id
            )

            asyncio.create_task(
                self.task_orchestrator.execute(task)
            )

            system_message = Message(content=self.get_task_started_message(intent.task_type, intent.intent_action), role=MessageRole.SYSTEM)

            try:

                conversation.add_message(system_message)

                source = self.context_source_factory.create(conversation)

                context = self.context_builder.build(source)

                output = await self.model_provider.chat(context)

            finally:
                conversation.remove_system_message(system_message)

            conversation.add_message(
                Message(
                    role=MessageRole.ASSISTANT,
                    content=output.content,
                )
            )

        self.conversation_store.save(conversation)

        return ChatServiceResponse(
            conversation_id=conversation.id,
            content=output.content,
        )

    def get_task_started_message(self, task_type: str, intent_action: str) -> str:
        message = self.prompt_provider.get("task_started_message").format(task_type=task_type, intent_action=intent_action)
        return message