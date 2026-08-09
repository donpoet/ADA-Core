from fastapi import FastAPI
from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from pydantic import BaseModel
from app.config import Settings
from app.conversation.context import ContextBuilder
from app.conversation.models import Conversation

app = FastAPI(
    title="ADA Core",
    version="0.1.0",
)

app_settings = Settings()

ollama = OllamaClient(base_url=app_settings.ollama_url, timeout=app_settings.ollama_timeout)
conversation = Conversation()
context_builder = ContextBuilder()
chat_service = ChatService(ollama_client=ollama, context_builder=context_builder)

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel): 
    response: str

@app.get("/")
async def root():
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
        converstaion=conversation,
        message=request.prompt,
    )

    return ChatResponse(
        response=response,
    )