import pytest
from unittest.mock import AsyncMock

from app.conversation.store import ConversationStore
from app.memory.service import MemoryService
from app.conversation.models import Conversation
from datetime import (
    datetime,
    UTC
)

@pytest.mark.asyncio
async def test_list_conversations():
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
    
    store = AsyncMock(spec=ConversationStore)
    store.list_conversations.return_value = [
        conversation1,
        conversation2,
        conversation3,
    ]

    memory_service = MemoryService(store)

    result = memory_service.list_conversations()

    assert len(result) == 3

    resutl_ids = {conversation.id for conversation in result}

    assert resutl_ids == {
        conversation1.id,
        conversation2.id,
        conversation3.id
    }


