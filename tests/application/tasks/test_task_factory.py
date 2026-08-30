from uuid import uuid4

from app.application.tasks.task_factory import TaskFactory
from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.tasks.enums import TaskType


def test_create_task():
    task_store = InMemoryTaskStore()
    task_factory = TaskFactory(task_store)

    conversation_id = uuid4()
    source_message_id = uuid4()

    task = task_factory.create_task(
        task_type=TaskType.WEAK_LLM,
        conversation_id=conversation_id,
        source_message_id=source_message_id,
    )

    assert task.type == TaskType.WEAK_LLM
    assert task.conversation_id == conversation_id
    assert task.source_message_ids == [source_message_id]

    stored_task = task_store.get_task(task.id)

    assert stored_task is not None
    assert stored_task.source_message_ids == [source_message_id]


def test_update_task():
    task_store = InMemoryTaskStore()
    task_factory = TaskFactory(task_store)

    task = task_store.create_task(
        TaskType.WEAK_LLM,
        uuid4(),
    )

    original_source_message_id = uuid4()
    new_source_message_id = uuid4()

    task.source_message_ids.append(original_source_message_id)
    task_store.save_task(task)

    task_factory.update_task(
        task,
        new_source_message_id,
    )

    assert task.source_message_ids == [
        original_source_message_id,
        new_source_message_id,
    ]

    stored_task = task_store.get_task(task.id)

    assert stored_task is not None
    assert stored_task.source_message_ids == [
        original_source_message_id,
        new_source_message_id,
    ]