from typing import TypeVar

from .event_publisher import EventPublisher
from .event_handler import EventHandler
from .models import Event

import asyncio

E = TypeVar("E", bound=Event)

class EventDispatcher(EventPublisher):

    def __init__(self):
        self._handlers: dict[type[Event], list[EventHandler]] = {}

    def register(
        self,
        event_type: type[E],
        handler: EventHandler[E],
    ) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish_event(self, event: E) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            asyncio.create_task(self._handle_event(event, handler))


    async def _handle_event(self, event: E, handler: EventHandler[E]) -> None:
        try:
            await handler.handle_event(event)
        except Exception as e:
            print(f"Error occurred while handling event: {e}")