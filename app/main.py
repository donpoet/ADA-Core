from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from pydantic import BaseModel
from app.config import Settings
from app.context.context import ContextBuilder
from app.conversation.sqlite_store import SQLiteConversationStore
from app.prompts.prompt_provider import PromptProvider
from uuid import UUID
from pathlib import Path
from sqlalchemy import create_engine

app = FastAPI(
    title="ADA Core",
    version="0.1.0",
)

app_settings = Settings()

ollama = OllamaClient(base_url=app_settings.ollama_url, timeout=app_settings.ollama_timeout)
db_engine = create_engine(app_settings.database_url)
conversation_store = SQLiteConversationStore(db_engine)
prompt_provider = PromptProvider(Path("app/prompts"))
context_builder = ContextBuilder(prompt_provider)
chat_service = ChatService(
    ollama_client=ollama, 
    context_builder=context_builder,
    conversation_store=conversation_store)

class ChatRequest(BaseModel):
    prompt: str
    conversation_id: UUID | None = None

class ChatResponse(BaseModel): 
    response: str
    conversation_id: UUID

app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
async def frontend():
    return FileResponse("web/index.html")

@app.get("/info")
async def info():
    return {
        "name": "ADA Core", 
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    ollama_healthy = await ollama.health()
    return {
        "status": "ok" if ollama_healthy else "degraded",
        "ollama_healthy": "ok" if ollama_healthy else "unavailable"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await chat_service.chat(
        conversation_id=request.conversation_id,
        message=request.prompt,
    )

    print(response.conversation_id)

    return ChatResponse(
        response=response.content,
        conversation_id= response.conversation_id,
    )