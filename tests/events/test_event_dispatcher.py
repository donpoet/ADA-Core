from app.events.event_handler import EventHandler
from app.events.event_dispatcher import EventDispatcher
from app.events.models import Event
import pytest
import asyncio

class TestEvent(Event):
    pass

class TestEventNotCalled(Event):
    pass

class TestEventHandler(EventHandler[TestEvent]):
    def __init__(self, calls):
        self.calls = calls
    
    async def handle_event(self, event: TestEvent) -> None:
        self.calls.append(event)

class TestEventHandlerWithError(EventHandler[TestEvent]):
    async def handle_event(self, event: TestEvent) -> None:
        raise Exception("Test exception")

class BlockingTestEventHandler(EventHandler[TestEvent]):
    def __init__(self, calls):
        self.calls = calls
        self.started = asyncio.Event()
        self.release_event = asyncio.Event()

    async def handle_event(self, event: TestEvent) -> None:
        self.calls.append(event)
        self.started.set()  # Signal that the handler has started processing
        await self.release_event.wait()  # Wait until released

    def release(self):
        self.release_event.set()  # Release the handler to finish processing

def test_event_dispatcher_register():
    calls = []
    dispatcher = EventDispatcher()
    handler = TestEventHandler(calls)

    dispatcher.register(TestEvent, handler)

    assert TestEvent in dispatcher._handlers
    assert handler in dispatcher._handlers[TestEvent]

def test_event_dispatcher_register_multiple_handlers():
    calls1 = []
    calls2 = []
    dispatcher = EventDispatcher()
    handler1 = TestEventHandler(calls1)
    handler2 = TestEventHandler(calls2)

    dispatcher.register(TestEvent, handler1)
    dispatcher.register(TestEvent, handler2)

    assert TestEvent in dispatcher._handlers
    assert handler1 in dispatcher._handlers[TestEvent]
    assert handler2 in dispatcher._handlers[TestEvent]

@pytest.mark.asyncio
async def test_event_dispatcher_calls_all_handlers():
    calls1 = []
    calls2 = []
    dispatcher = EventDispatcher()
    handler1 = TestEventHandler(calls1)
    handler2 = TestEventHandler(calls2)

    dispatcher.register(TestEvent, handler1)
    dispatcher.register(TestEvent, handler2)

    event = TestEvent()
    await dispatcher.publish_event(event)

    await wait_for_calls(calls1)
    await wait_for_calls(calls2)

    assert len(calls1) == 1
    assert calls1[0] == event
    assert len(calls2) == 1
    assert calls2[0] == event

@pytest.mark.asyncio
async def test_event_with_no_registered_handlers():
    dispatcher = EventDispatcher()
    event = TestEvent()

    await dispatcher.publish_event(event)

@pytest.mark.asyncio
async def test_event_dispatcher_does_not_call_unregistered_handlers():
    dispatcher = EventDispatcher()
    not_called_handler = TestEventHandler([])
    called_handler = TestEventHandler([])

    dispatcher.register(TestEvent, called_handler)
    dispatcher.register(TestEventNotCalled, not_called_handler)

    event = TestEvent()
    await dispatcher.publish_event(event)

    await wait_for_calls(called_handler.calls)
    with pytest.raises(AssertionError):
        await wait_for_calls(not_called_handler.calls)

    assert len(not_called_handler.calls) == 0
    assert len(called_handler.calls) == 1
    assert called_handler.calls[0] == event

@pytest.mark.asyncio
async def test_event_dispatcher_handler_exception_does_not_stop_other_handlers():
    calls = []
    dispatcher = EventDispatcher()
    handler_with_error = TestEventHandlerWithError()
    normal_handler = TestEventHandler(calls)

    dispatcher.register(TestEvent, handler_with_error)
    dispatcher.register(TestEvent, normal_handler)

    event = TestEvent()
    await dispatcher.publish_event(event)

    await wait_for_calls(calls)

    assert len(calls) == 1
    assert calls[0] == event

@pytest.mark.asyncio
async def test_event_dispatcher_publish_does_not_block():
    dispatcher = EventDispatcher()
    handler = BlockingTestEventHandler([])

    dispatcher.register(TestEvent, handler)

    event = TestEvent()
    await dispatcher.publish_event(event)

    await handler.started.wait()  # Wait until the handler has started processing

    assert not handler.release_event.is_set()  # Ensure the handler is still waiting

    handler.release()  # Release the handler to finish processing

async def wait_for_calls(calls):
    for i in range(100):
        if len(calls) > 0:
            return
        await asyncio.sleep(0.001)

    raise AssertionError("Handler was not called")