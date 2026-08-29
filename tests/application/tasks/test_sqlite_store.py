from sqlalchemy.orm import Session

from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.conversation.models import Message, MessageRole
from app.database.schema import TaskModel

from app.tasks.models import Task
from app.tasks.enums import TaskType, TaskStatus

from datetime import datetime, UTC
from uuid import uuid4

import pytest

def test_create_task(db_engine):
    store = SQLiteTaskStore(db_engine)

    conversation_id = uuid4()

    task = store.create_task(TaskType.WEAK_LLM, conversation_id)

    assert task.id is not None
    assert task.conversation_id == conversation_id
    assert task.type is TaskType.WEAK_LLM
    assert task.status is TaskStatus.OPEN
    assert task.source_message_ids == []
    assert task.created_at is not None
    assert task.completed_at is None

    with Session(db_engine) as session:
        stored = session.get(
            TaskModel,
            str(task.id)
        )

        assert stored is not None
        assert stored.id == str(task.id)
        assert stored.conversation_id == str(conversation_id)
        assert stored.type is TaskType.WEAK_LLM
        assert stored.status is TaskStatus.OPEN
        assert stored.source_messages == []
        assert stored.created_at is not None
        assert stored.completed_at is None

def test_get_task(db_engine):
    conversation_store = SQLiteConversationStore(db_engine)
    conversation = conversation_store.create()
    task_id = uuid4()

    with Session(db_engine) as session:
        task = TaskModel(
            id=str(task_id),
            conversation_id=str(conversation.id),
            type=TaskType.WEAK_LLM,
            status=TaskStatus.OPEN,
            created_at=datetime.now(UTC),
            completed_at=None,
        )

        session.add(task)
        session.commit()
        assert session.get(
            TaskModel,
            str(task_id)
        ) is not None
        
    store = SQLiteTaskStore(db_engine)

    result = store.get_task(task_id)

    assert isinstance(result, Task)
    assert result.id == task_id
    assert result.conversation_id == conversation.id
    assert result.type is TaskType.WEAK_LLM
    assert result.status is TaskStatus.OPEN
    assert result.source_message_ids == []
    assert result.created_at is not None
    assert result.completed_at is None

def test_save_task_with_new_source_messages(db_engine):
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine)

    conversation = conversation_store.create()
    message1 = Message(
        role=MessageRole.USER,
        content="Hallo Ada!",
    )
    message2 = Message(
        role=MessageRole.ASSISTANT,
        content="Hallo! Wie kann ich dir helfen?"
    )
    conversation.add_message(message1)
    conversation.add_message(message2)
    conversation_store.save(conversation)

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    task.source_message_ids.append(message1.id)
    task.source_message_ids.append(message2.id)

    task_store.save_task(task)

    task = task_store.get_task(task.id)

    assert set(task.source_message_ids) == {message1.id, message2.id}

def test_save_task_with_altered_source_messages(db_engine):
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine)

    conversation = conversation_store.create()
    message1 = Message(
        role=MessageRole.USER,
        content="Hallo Ada!",
    )
    message2 = Message(
        role=MessageRole.ASSISTANT,
        content="Hallo! Wie kann ich dir helfen?"
    )
    message3 = Message(
        role=MessageRole.SYSTEM,
        content="system-prompt"
    )
    conversation.add_message(message1)
    conversation.add_message(message2)
    conversation.add_message(message3)
    conversation_store.save(conversation)

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    task.source_message_ids.append(message1.id)
    task.source_message_ids.append(message2.id)

    task_store.save_task(task)

    task = task_store.get_task(task.id)

    assert message1.id in task.source_message_ids
    assert message2.id in task.source_message_ids
    assert message3.id not in task.source_message_ids

    task.source_message_ids = [message2.id, message3.id]

    task_store.save_task(task)

    task = task_store.get_task(task.id)

    assert message3.id in task.source_message_ids
    assert message2.id in task.source_message_ids
    assert message1.id not in task.source_message_ids

def test_list_tasks(db_engine):
    store = SQLiteTaskStore(db_engine)

    conversation_id = uuid4()

    task1 = store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = store.create_task(TaskType.WEAK_LLM, conversation_id)

    expected_task_ids = [task1.id, task2.id, task3.id]

    results = store.list_tasks()

    result_ids = [result.id for result in results]

    assert set(result_ids) == set(expected_task_ids)

def test_raise_value_error_for_unknown_task(db_engine):
    store = SQLiteTaskStore(db_engine)

    with pytest.raises(ValueError):
        store.get_task(uuid4())