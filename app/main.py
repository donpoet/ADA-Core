from fastapi import FastAPI
from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from pydantic import BaseModel

app = FastAPI(
    title="ADA Core",
    version="0.1.0",
)

ollama = OllamaClient(base_url="http://ada:11434")
chat_service = ChatService(ollama_client=ollama)

class ChatRequest(BaseModel):
    model: str = "qwen3:4b"
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
        model=request.model, 
        prompt=request.prompt
    )

    return ChatResponse(
        response=response,
    )