from sqlalchemy.orm import Session

from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.conversation.models import Message, MessageRole
from app.database.schema import TaskModel, TaskExecutionModel

from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus

from app.application.artifacts.stores.artifact_store import ArtifactStore

from app.ollama.models import OllamaContextOutput

from datetime import datetime, UTC
from uuid import uuid4, UUID

import pytest
from unittest.mock import AsyncMock

from app.dependencies import task_component_registry

from datetime import datetime, UTC, timedelta

def test_create_task(db_engine):
    store = SQLiteTaskStore(db_engine, task_component_registry)

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
        
    store = SQLiteTaskStore(db_engine, task_component_registry)

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
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

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
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

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
    store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation_id = uuid4()

    task1 = store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = store.create_task(TaskType.WEAK_LLM, conversation_id)

    expected_task_ids = [task1.id, task2.id, task3.id]

    results = store.list_tasks()

    result_ids = [result.id for result in results]

    assert set(result_ids) == set(expected_task_ids)

def test_raise_value_error_for_unknown_task(db_engine):
    store = SQLiteTaskStore(db_engine, task_component_registry)

    with pytest.raises(ValueError):
        store.get_task(uuid4())

def test_filter_tasks_one_filter(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation_id = uuid4()
    conversation_id2 = uuid4()

    task1 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)

    expected_task_ids1 = [task1.id, task2.id]
    expected_task_ids2 = [task3.id]

    results1 = task_store.filter_tasks(conversation_id=conversation_id)
    results2 = task_store.filter_tasks(conversation_id=conversation_id2)

    result_ids1 = [result.id for result in results1]
    result_ids2 = [result.id for result in results2]

    assert set(result_ids1) == set(expected_task_ids1)
    assert set(result_ids2) == set(expected_task_ids2)

def test_filter_tasks_multiple_filters(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation_id = uuid4()
    conversation_id2 = uuid4()

    task1 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)
    task4 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task5 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task6 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)
    task7 = task_store.create_task(TaskType.HOME_AUTOMATION, conversation_id)
    task8 = task_store.create_task(TaskType.HOME_AUTOMATION, conversation_id2)

    task1.complete()
    task2.complete()
    task3.complete()
    task7.complete()

    task_store.save_task(task1)
    task_store.save_task(task2)
    task_store.save_task(task3)
    task_store.save_task(task7)

    expected_task_ids1 = [task4.id, task5.id]
    expected_task_ids2 = [task1.id, task2.id]
    expected_task_ids3 = [task6.id]
    expected_task_ids4 = [task3.id]
    expected_task_ids5 = [task8.id]
    expected_task_ids6 = [task7.id]

    results1 = task_store.filter_tasks(conversation_id=conversation_id, status=TaskStatus.OPEN, task_type=TaskType.WEAK_LLM)
    results2 = task_store.filter_tasks(conversation_id=conversation_id, status=TaskStatus.COMPLETED, task_type=TaskType.WEAK_LLM)
    results3 = task_store.filter_tasks(conversation_id=conversation_id2, status=TaskStatus.OPEN, task_type=TaskType.WEAK_LLM)
    results4 = task_store.filter_tasks(conversation_id=conversation_id2, status=TaskStatus.COMPLETED, task_type=TaskType.WEAK_LLM)
    results5 = task_store.filter_tasks(conversation_id=conversation_id2, status=TaskStatus.OPEN, task_type=TaskType.HOME_AUTOMATION)
    results6 = task_store.filter_tasks(conversation_id=conversation_id, status=TaskStatus.COMPLETED, task_type=TaskType.HOME_AUTOMATION)

    result_ids1 = [result.id for result in results1]
    result_ids2 = [result.id for result in results2]
    result_ids3 = [result.id for result in results3]
    result_ids4 = [result.id for result in results4]
    result_ids5 = [result.id for result in results5]
    result_ids6 = [result.id for result in results6]


    assert set(result_ids1) == set(expected_task_ids1)
    assert set(result_ids2) == set(expected_task_ids2)
    assert set(result_ids3) == set(expected_task_ids3)
    assert set(result_ids4) == set(expected_task_ids4)
    assert set(result_ids5) == set(expected_task_ids5)
    assert set(result_ids6) == set(expected_task_ids6)

def test_filter_tasks_with_datetime_filter(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation_id = uuid4()
    conversation_id2 = uuid4()

    task1 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)
    task4 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task5 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task6 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)

    task1.complete()
    task2.complete()
    task3.complete()

    task_store.save_task(task1)
    task_store.save_task(task2)
    task_store.save_task(task3)

    expected_task_ids1 = []
    expected_task_ids2 = [task1.id, task2.id, task3.id]
    expected_task_ids3 = [task1.id, task2.id, task3.id]
    expected_task_ids4 = []
    expected_task_ids5 = []
    expected_task_ids6 = [task1.id, task2.id, task3.id, task4.id, task5.id, task6.id]
    expected_task_ids7 = [task1.id, task2.id, task3.id, task4.id, task5.id, task6.id]
    expected_task_ids8 = []
    expected_task_ids9 = [task1.id, task2.id, task3.id]
    expected_task_ids10 = []
    expected_task_ids11 = [task1.id, task2.id, task3.id, task4.id, task5.id, task6.id]
    expected_task_ids12 = []

    before_today = datetime.now(UTC) - timedelta(days=1)
    after_today = datetime.now(UTC) + timedelta(days=1)

    results1 = task_store.filter_tasks(completed_before=before_today)
    results2 = task_store.filter_tasks(completed_before=after_today)
    results3 = task_store.filter_tasks(completed_after=before_today)
    results4 = task_store.filter_tasks(completed_after=after_today)
    results5 = task_store.filter_tasks(created_before=before_today)
    results6 = task_store.filter_tasks(created_before=after_today)
    results7 = task_store.filter_tasks(created_after=before_today)
    results8 = task_store.filter_tasks(created_after=after_today)
    results9 = task_store.filter_tasks(completed_before=datetime.now(UTC))
    results10 = task_store.filter_tasks(completed_after=datetime.now(UTC))
    results11 = task_store.filter_tasks(created_before=datetime.now(UTC))
    results12 = task_store.filter_tasks(created_after=datetime.now(UTC))

    result_ids1 = [result.id for result in results1]
    result_ids2 = [result.id for result in results2]
    result_ids3 = [result.id for result in results3]
    result_ids4 = [result.id for result in results4]
    result_ids5 = [result.id for result in results5]
    result_ids6 = [result.id for result in results6]
    result_ids7 = [result.id for result in results7]
    result_ids8 = [result.id for result in results8]
    result_ids9 = [result.id for result in results9]
    result_ids10 = [result.id for result in results10]
    result_ids11 = [result.id for result in results11]
    result_ids12 = [result.id for result in results12]



    assert set(result_ids1) == set(expected_task_ids1)
    assert set(result_ids2) == set(expected_task_ids2)
    assert set(result_ids3) == set(expected_task_ids3)
    assert set(result_ids4) == set(expected_task_ids4)
    assert set(result_ids5) == set(expected_task_ids5)
    assert set(result_ids6) == set(expected_task_ids6)
    assert set(result_ids7) == set(expected_task_ids7)
    assert set(result_ids8) == set(expected_task_ids8)
    assert set(result_ids9) == set(expected_task_ids9)
    assert set(result_ids10) == set(expected_task_ids10)
    assert set(result_ids11) == set(expected_task_ids11)
    assert set(result_ids12) == set(expected_task_ids12)         

def test_filter_tasks_no_filters(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation_id = uuid4()
    conversation_id2 = uuid4()

    task1 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task2 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task3 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)
    task4 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task5 = task_store.create_task(TaskType.WEAK_LLM, conversation_id)
    task6 = task_store.create_task(TaskType.WEAK_LLM, conversation_id2)

    task1.complete()
    task2.complete()
    task3.complete()

    expected_task_ids = [task1.id, task2.id, task3.id, task4.id, task5.id, task6.id]

    results = task_store.filter_tasks()

    result_ids = [result.id for result in results]

    assert set(result_ids) == set(expected_task_ids)

def test_filter_tasks_no_result(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    result = task_store.filter_tasks(conversation_id=uuid4())
    
    assert result == []

def test_get_task_execution(db_engine):
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    with Session(db_engine) as session:
        task_execution_model = TaskExecutionModel(
            id=str(uuid4()),
            task_id=str(task.id),
            status=TaskExecutionStatus.PENDING,
            context={
                "messages":[
                    {
                        "role":"user",
                        "content":"Hallo Ada!"
                    }
                ]
            },
            started_at=None,
            finished_at=None,
        )
        session.add(task_execution_model)
        session.commit()

        get_result = task_store.get_task_execution(UUID(task_execution_model.id))

        assert isinstance(get_result, TaskExecution)
        assert get_result.id == UUID(task_execution_model.id)
        assert get_result.task_id == UUID(task_execution_model.task_id)
        assert get_result.status is task_execution_model.status
        assert get_result.context.model_dump() == task_execution_model.context
        assert get_result.started_at is None
        assert get_result.finished_at is None

def test_save_task_execution(db_engine):
    execution_facotry = task_component_registry.get(TaskType.WEAK_LLM).execution_factory

    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)
    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    task_execution = execution_facotry.create(
        task.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_store.save_task_execution(task_execution)

    get_result = task_store.get_task_execution(task_execution.id)

    assert isinstance(get_result, TaskExecution)
    assert get_result.id == task_execution.id
    assert get_result.task_id == task_execution.task_id
    assert get_result.status is task_execution.status
    assert get_result.context == task_execution.context
    assert get_result.started_at is None
    assert get_result.finished_at is None

def test_save_modified_task_execution(db_engine):
    execution_facotry = task_component_registry.get(TaskType.WEAK_LLM).execution_factory

    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)
    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    task_execution = execution_facotry.create(
        task.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_store.save_task_execution(task_execution)

    task_execution.start()
    task_execution.complete()

    task_store.save_task_execution(task_execution)

    get_result = task_store.get_task_execution(task_execution.id)

    assert isinstance(get_result, TaskExecution)
    assert get_result.id == task_execution.id
    assert get_result.task_id == task_execution.task_id
    assert get_result.status is task_execution.status
    assert get_result.context == task_execution.context
    assert get_result.started_at is not None
    assert get_result.finished_at is not None

def test_list_task_executions(db_engine):
    execution_facotry = task_component_registry.get(TaskType.WEAK_LLM).execution_factory

    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)
    conversation = conversation_store.create()

    task1 = task_store.create_task(TaskType.WEAK_LLM, conversation.id)
    task2 = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    task_execution1 = execution_facotry.create(
        task1.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_execution2 = execution_facotry.create(
        task1.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_execution3 = execution_facotry.create(
        task1.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_execution4 = execution_facotry.create(
        task2.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Hallo Ada!"
                }
            ]
        )
    )

    task_store.save_task_execution(task_execution1)
    task_store.save_task_execution(task_execution2)
    task_store.save_task_execution(task_execution3)
    task_store.save_task_execution(task_execution4)

    expected_ids1 = [task_execution1.id, task_execution2.id, task_execution3.id]
    expected_ids2 = [task_execution4.id]

    results1 = task_store.list_task_executions(task1.id)

    result_ids1 = [result.id for result in results1]

    results2 = task_store.list_task_executions(task2.id)

    result_ids2 = [result.id for result in results2]

    assert set(result_ids1) == set(expected_ids1)
    assert set(result_ids2) == set(expected_ids2)

def test_raise_value_error_for_unknown_task_execution(db_engine):
    store = SQLiteTaskStore(db_engine, task_component_registry)

    with pytest.raises(ValueError):
        store.get_task_execution(uuid4())

def test_get_empty_list_for_task_without_executions(db_engine):
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)
    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    results = task_store.list_task_executions(task.id)

    assert results == []