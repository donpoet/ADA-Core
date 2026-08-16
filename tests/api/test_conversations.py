from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import(
    get_memory_service
)
from app.memory.service import MemoryService
from app.conversation.sqlite_store import SQLiteConversationStore
from app.conversation.models import Conversation
from datetime import (
    datetime,
    UTC
)

def test_list_conversations_api(db_engine):
    store = SQLiteConversationStore(db_engine)
    memory_service = MemoryService(store)

    conversation1 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conversation2 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    conversation3 = Conversation(
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    store.save(conversation1)
    store.save(conversation2)
    store.save(conversation3)

    app.dependency_overrides[get_memory_service] = (
        lambda: memory_service
    )

    try:
        client = TestClient(app)
        response = client.get("/conversations")

        assert response.status_code == 200

        data = response.json()

        assert len(data["conversations"]) == 3

        returned_ids = {
            item["id"]
            for item in data["conversations"]
        }

        expected_ids = {
            str(conversation1.id),
            str(conversation2.id),
            str(conversation3.id),
        }

        assert returned_ids == expected_ids

    finally:
        app.dependency_overrides.clear()
