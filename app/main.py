from fastapi import FastAPI
from app.ollama.OllamaClient import OllamaClient

app = FastAPI(
    title="ADA Core",
    version="0.1.0",
)

ollama = OllamaClient(base_url="http://ada:11434")

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