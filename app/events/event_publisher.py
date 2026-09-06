from abc import ABC, abstractmethod
from .models import Event

class EventPublisher(ABC):
    @abstractmethod
    async def publish_event(self, event: Event) -> None:
        pass