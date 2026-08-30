from pathlib import Path
from sqlalchemy import create_engine

from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from app.config import Settings
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from app.memory.service import MemoryService
from app.ollama.context_builder import OllamaContextBuilder
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.ollama.model_provider import OllamaModelProvider
from app.application.artifacts.stores.artifact_sqlite_store import SQLiteArtifactStore
from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.tasks.task_results.stores.sqlite_store import SQLiteTaskResultStore
from app.application.tasks.component_registry import TaskComponentRegistry
from app.application.tasks.ochestrator import TaskOrchestrator
from app.application.tasks.task_factory import TaskFactory

######################## General Purpose Components ###################################

####### Main:
app_settings = Settings()
db_engine = create_engine(app_settings.database_url)
prompt_provider = PromptProvider(Path("app/prompts"))
task_component_registry = TaskComponentRegistry()
task

####### Stores:
artifact_store = SQLiteArtifactStore(db_engine)
conversation_store = SQLiteConversationStore(db_engine)
task_store = SQLiteTaskStore(db_engine, task_component_registry)
task_result_store = SQLiteTaskResultStore(db_engine)

####### Ollama:
ollama_client = OllamaClient(base_url=app_settings.ollama_url, timeout=app_settings.ollama_timeout)
ollama_context_builder = OllamaContextBuilder(prompt_provider)
ollama_chat_context_source_factory = OllamaChatContextSourceFactory()
ollama_model_provider = OllamaModelProvider(ollama_client, app_settings.default_model)

####### Services:
task_orchestrator = TaskOrchestrator(task_store, task_component_registry, task_result_store)
task_factory = TaskFactory(task_store)
intent_recognizer = none #TODO
chat_service = ChatService( 
    context_builder=ollama_context_builder,
    conversation_store=conversation_store,
    model_provider=ollama_model_provider,
    context_source_factory=ollama_chat_context_source_factory,
    intent_recognizer=intent_recognizer,
    task_factory=task_factory,
    task_orchestrator=task_orchestrator)  
memory_service = MemoryService(conversation_store)

####### API Interfaces:
def get_ollama_client() -> OllamaClient:
    return ollama_client

def get_chat_service() -> ChatService:
    return chat_service

def get_memory_service() -> MemoryService:
    return memory_service


######################## Task Registry Components #####################################

from app.application.tasks.components import TaskComponents
from app.tasks.enums import TaskType
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.ollama.context_builder import OllamaContextBuilder
from app.prompts.prompt_provider import PromptProvider
from app.application.tasks.executions.weak_llm.execution_factory import WeakLLMTaskExecutionFactory
from app.chat.context_input_provider import ChatContextInputProvider

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