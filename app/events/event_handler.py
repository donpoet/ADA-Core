from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .models import Event

E = TypeVar("E", bound=Event)

class EventHandler(ABC, Generic[E]):
    @abstractmethod
    async def handle_event(self, event: E) -> None:
        pass