from pathlib import Path
from sqlalchemy import create_engine

from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from app.config import Settings
from app.conversation.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from app.memory.service import MemoryService
from app.ollama.context_builder import OllamaContextBuilder
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.ollama.model_provider import OllamaModelProvider
from app.application.artifacts.stores.artifact_memory_store import InMemoryArtifactStore

app_settings = Settings()

######################## General Purpose Components ###################################

ollama_client = OllamaClient(base_url=app_settings.ollama_url, timeout=app_settings.ollama_timeout)
db_engine = create_engine(app_settings.database_url)
conversation_store = SQLiteConversationStore(db_engine)
prompt_provider = PromptProvider(Path("app/prompts"))
memory_service = MemoryService(conversation_store)
ollama_context_builder = OllamaContextBuilder(prompt_provider)
ollama_chat_context_source_factory = OllamaChatContextSourceFactory()
ollama_model_provider = OllamaModelProvider(ollama_client, app_settings.default_model)
chat_service = ChatService( 
    context_builder=ollama_context_builder,
    conversation_store=conversation_store,
    model_provider=ollama_model_provider,
    context_source_factory=ollama_chat_context_source_factory)  
artifact_store = InMemoryArtifactStore()

def get_ollama_client() -> OllamaClient:
    return ollama_client

def get_chat_service() -> ChatService:
    return chat_service

def get_memory_service() -> MemoryService:
    return memory_service

######################## Task Registry Components #####################################

from app.application.tasks.component_registry import TaskComponentRegistry
from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.components import TaskComponents
from app.tasks.enums import TaskType
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.ollama.context_builder import OllamaContextBuilder
from app.prompts.prompt_provider import PromptProvider
from app.application.tasks.executions.weak_llm.execution_factory import WeakLLMTaskExecutionFactory
from app.chat.context_input_provider import ChatContextInputProvider


task_component_registry = TaskComponentRegistry()

#---------- Weak LLM Task ------------#

weak_llm_model_provider = OllamaModelProvider(ollama_client, "qwen3:1.7b")

task_component_registry.register(
    TaskType.WEAK_LLM,
    TaskComponents(
        context_source_factory=ollama_chat_context_source_factory,
        context_builder=OllamaContextBuilder(prompt_provider),
        execution_factory=WeakLLMTaskExecutionFactory(artifact_store, prompt_provider),
        context_input_provider=ChatContextInputProvider(conversation_store),
    )
)