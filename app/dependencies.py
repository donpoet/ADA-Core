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

app_settings = Settings()

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

def get_ollama_client() -> OllamaClient:
    return ollama_client

def get_chat_service() -> ChatService:
    return chat_service

def get_memory_service() -> MemoryService:
    return memory_service