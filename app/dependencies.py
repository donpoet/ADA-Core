from pathlib import Path
from sqlalchemy import create_engine

from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from app.config import Settings
from app.context.context import ContextBuilder
from app.conversation.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from app.memory.service import MemoryService

app_settings = Settings()

ollama = OllamaClient(base_url=app_settings.ollama_url, timeout=app_settings.ollama_timeout)
db_engine = create_engine(app_settings.database_url)
conversation_store = SQLiteConversationStore(db_engine)
prompt_provider = PromptProvider(Path("app/prompts"))
context_builder = ContextBuilder(prompt_provider)
memory_service = MemoryService(conversation_store)
chat_service = ChatService(
    ollama_client=ollama, 
    context_builder=context_builder,
    conversation_store=conversation_store)  

def get_ollama() -> OllamaClient:
    return ollama

def get_chat_service() -> ChatService:
    return chat_service

def get_memory_service() -> MemoryService:
    return memory_service