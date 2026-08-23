from app.tasks.models import TaskResult
from app.tasks.enums import TaskResultStatus
from app.application.tasks.task_results.stores.memory_store import InMemoryTaskResultStore

from uuid import uuid4

def test_create_and_get_task_result():
    store = InMemoryTaskResultStore()

    task_execution_id = uuid4()

    task_result = TaskResult(
        task_execution_id=task_execution_id,
        status=TaskResultStatus.SUCCESS,
        error_code=None
    )

    store.save_task_result(task_result)

    result = store.get_task_result(task_execution_id)

    assert result is task_result

def test_save_task():
    store = InMemoryTaskResultStore()

    task_execution_id = uuid4()

    task_result = TaskResult(
        task_execution_id=task_execution_id,
        status=TaskResultStatus.SUCCESS,
        error_code=None
    )

    store.save_task_result(task_result)

    task_result.status = TaskResultStatus.CANCELLED

    store.save_task_result(task_result)

    result = store.get_task_result(task_execution_id)

    assert result is task_result
    assert result.id == task_result.id
    assert result.task_execution_id == task_execution_id
    assert result.status == task_result.status
    assert result.error_code is None



def test_get_unknown_task_returns_none():
    store = InMemoryTaskResultStore()

    result = store.get_task_result(uuid4())

    assert result is None
