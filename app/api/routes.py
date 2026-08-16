from fastapi import (
    APIRouter,
    Depends
)
from app.api.models import(
    ChatRequest,
    ChatResponse,
    ConversationsListResponse,
    ConversationListItem,
    ConversationMessageItem,
    ConversationResponse
)
from app.ollama.ollama_client import OllamaClient
from app.chat.service import ChatService
from app.memory.service import MemoryService
from fastapi.responses import FileResponse
from app.dependencies import(
    get_chat_service,
    get_memory_service, 
    get_ollama
)
from uuid import UUID

router = APIRouter()

@router.get("/")
async def frontend():
    return FileResponse("web/index.html")

@router.get("/info")
async def info():
    return {
        "name": "ADA Core", 
        "version": "0.2.0"
    }

@router.get("/health")
async def health(ollama: OllamaClient = Depends(get_ollama)):
    ollama_healthy = await ollama.health()
    return {
        "status": "ok" if ollama_healthy else "degraded",
        "ollama_healthy": "ok" if ollama_healthy else "unavailable"
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    response = await chat_service.chat(
        conversation_id=request.conversation_id,
        message=request.prompt,
    )

    return ChatResponse(
        response=response.content,
        conversation_id= response.conversation_id,
    )

@router.get("/conversations", response_model=ConversationsListResponse)
def list_conversations(memory_service: MemoryService = Depends(get_memory_service)):
    result = memory_service.list_conversations()

    return ConversationsListResponse(
        conversations=[
            ConversationListItem(
                id=conversation.id,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            ) 
            for conversation in result
        ]
    )

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def list_conversations(conversation_id:UUID, memory_service: MemoryService = Depends(get_memory_service)):
    result = memory_service.get_conversation(conversation_id)

    return ConversationResponse(
        id=result.id,
        title=result.title,
        created_at=result.created_at,
        updated_at=result.updated_at,
        messages=[
            ConversationMessageItem(
                id=message.id,
                role=message.role,
                content=message.content
            )
            for message in result.messages
        ]
    )