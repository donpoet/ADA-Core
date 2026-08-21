from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import(
    get_memory_service
)
from app.memory.service import MemoryService
from app.conversation.memory_store import InMemoryConversationStore
from app.conversation.models import Conversation, Message, MessageRole
from datetime import (
    datetime,
    UTC
)

def test_list_conversations_api():
    store = InMemoryConversationStore()
    memory_service = MemoryService(store)

    conversation1 = store.create()

    conversation1.add_message(
        message=Message(
            role=MessageRole.USER,
            content="Hi Ada!"
        )
    )

    conversation_id = conversation1.id

    store.save(conversation1)
    
    app.dependency_overrides[get_memory_service] = (
        lambda: memory_service
    )

    try:
        client = TestClient(app)
        response = client.get(f"/conversations/{conversation_id}")

        assert response.status_code == 200

        data = response.json()

        assert len(data["messages"]) == 1

        assert data["id"] == str(conversation1.id)
        assert data["messages"][0]["content"] == "Hi Ada!"

    finally:
        app.dependency_overrides.clear()