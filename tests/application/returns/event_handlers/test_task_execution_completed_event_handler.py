from app.application.returns.event_handlers.task_execution_completed_event_handler import TaskExecutionCompletedEventHandler
from app.events.models import TaskExecutionCompletedEvent
from app.application.returns.return_decision_service import ReturnDecisionService
from app.returns.enums import ReturnAction

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

@pytest.mark.asyncio
async def test_handle_event():
    decision_service = AsyncMock(ReturnDecisionService)
    decision_service.decide.return_value = ReturnAction.RESPOND_NOW

    event_handler = TaskExecutionCompletedEventHandler(decision_service)

    event = TaskExecutionCompletedEvent(
        task_id=uuid4(),
        task_execution_id=uuid4(),
        task_result_id=uuid4()
    )

    await event_handler.handle_event(event)

    decision_service.decide.assert_awaited_once_with(event)