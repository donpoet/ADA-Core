from app.application.tasks.task_results.stores.sqlite_store import SQLiteTaskResultStore, DuplicateTaskResultError
from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore

from app.database.schema import TaskResultModel

from app.tasks.enums import TaskType, TaskResultStatus
from app.tasks.models import TaskResult
from app.ollama.models import OllamaContextOutput

from app.dependencies import task_component_registry

from sqlalchemy.orm import Session

from uuid import uuid4

import pytest

def test_get_task_result(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)

    conversation = conversation_store.create()
    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)
    task_execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_result = TaskResult(
        task_execution_id=task_execution.id,
        status=TaskResultStatus.SUCCESS,
        error_code=None,
    )

    conversation_store.save(conversation)
    task_store.save_task(task)
    task_store.save_task_execution(task_execution)

    with Session(db_engine) as session:
        task_result_model = TaskResultModel(
            id=str(task_result.id),
            task_execution_id=str(task_execution.id),
            status=task_result.status,
            error_code=task_result.error_code,
        )

        session.add(task_result_model)
        session.commit()

    get_result = task_result_store.get_task_result(task_execution.id)

    assert isinstance(get_result, TaskResult)
    assert get_result.id == task_result.id
    assert get_result.task_execution_id == task_result.task_execution_id
    assert get_result.status == task_result.status
    assert get_result.error_code == task_result.error_code

def test_get_task_result_returns_none_for_no_result(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)

    conversation = conversation_store.create()
    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)
    task_execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    conversation_store.save(conversation)
    task_store.save_task(task)
    task_store.save_task_execution(task_execution)

    get_result = task_result_store.get_task_result(task_execution.id)

    assert get_result is None

def test_get_task_result_raises_value_error_unknown_execution(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)
    with pytest.raises(ValueError):
        task_result_store.get_task_result(uuid4())

def test_save_task_result(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)

    conversation = conversation_store.create()
    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)
    task_execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_result = TaskResult(
        task_execution_id=task_execution.id,
        status=TaskResultStatus.SUCCESS,
        error_code=None,
    )

    conversation_store.save(conversation)
    task_store.save_task(task)
    task_store.save_task_execution(task_execution)

    task_result_store.save_task_result(task_result)

    get_result = task_result_store.get_task_result(task_execution.id)

    assert isinstance(get_result, TaskResult)
    assert get_result.id == task_result.id
    assert get_result.task_execution_id == task_result.task_execution_id
    assert get_result.status == task_result.status
    assert get_result.error_code == task_result.error_code

def test_save_task_result_raises_duplicate_error_for_existing_result_on_execution(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)
    conversation_store = SQLiteConversationStore(db_engine)

    conversation = conversation_store.create()
    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)
    task_execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_result = TaskResult(
        task_execution_id=task_execution.id,
        status=TaskResultStatus.SUCCESS,
        error_code=None,
    )

    conversation_store.save(conversation)
    task_store.save_task(task)
    task_store.save_task_execution(task_execution)

    task_result_store.save_task_result(task_result)

    task_result.error_code="some error"

    with pytest.raises(DuplicateTaskResultError):
        task_result_store.save_task_result(task_result)

def test_save_task_result_raise_value_error_if_execution_does_not_exist(db_engine):
    task_result_store = SQLiteTaskResultStore(db_engine)

    task_result = TaskResult(
        task_execution_id=uuid4(),
        status=TaskResultStatus.SUCCESS,
        error_code=None,
    )

    with pytest.raises(ValueError):
        task_result_store.save_task_result(task_result)
