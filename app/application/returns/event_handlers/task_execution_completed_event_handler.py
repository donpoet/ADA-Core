from app.events.event_handler import EventHandler
from app.events.models import TaskExecutionCompletedEvent
from app.application.returns.return_decision_service import ReturnDecisionService
class TaskExecutionCompletedEventHandler(EventHandler[TaskExecutionCompletedEvent]):
    
    def __init__(self, return_decision_service: ReturnDecisionService):
        self._return_decision_service = return_decision_service
    
    async def handle_event(self, event: TaskExecutionCompletedEvent) -> None:
        decision = await self._return_decision_service.decide(event)

        # some logging