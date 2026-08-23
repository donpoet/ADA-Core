from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus
from uuid import uuid4, UUID
from datetime import (
    datetime,
    UTC
)

class TestTaskExecution(TaskExecution):
    def execute(self):
        pass

def test_create_and_get_task():
    store = InMemoryTaskStore()

    task = store.create_task(TaskType.WEAK_LLM, uuid4())

    result = store.get_task(task.id)

    assert result is task

def test_save_task():
    store = InMemoryTaskStore()

    task = store.create_task(TaskType.WEAK_LLM, uuid4())
    
    store.save_task(task)

    result = store.get_task(task.id)

    assert result is task
    assert result.id is not None
    assert result.id == task.id
    assert result.conversation_id == task.conversation_id
    assert result.created_at is not None
    assert result.completed_at is None
    assert result.status == TaskStatus.OPEN
    assert result.source_message_ids == []



def test_get_unknown_task_returns_none():
    store = InMemoryTaskStore()

    result = store.get_task(uuid4())

    assert result is None

def test_list_tasks():
    task1 = Task(
        type=TaskType.WEAK_LLM,
        conversation_id=uuid4()
    )
    task2 = Task(
        type=TaskType.WEAK_LLM,
        conversation_id=uuid4()
    )
    task3 = Task(
        type=TaskType.WEAK_LLM,
        conversation_id=uuid4()
    )

    store = InMemoryTaskStore()

    store.save_task(task1)
    store.save_task(task2)
    store.save_task(task3)

    result = store.list_tasks()

    assert len(result) == 3

    resutl_ids = {task.id for task in result}

    assert resutl_ids == {
        task1.id,
        task2.id,
        task3.id
    }


def test_create_and_get_task_execution():
    store = InMemoryTaskStore()

    task_execution = TestTaskExecution(
        task_id=uuid4(),
        context=object(),
    )

    store.save_task_execution(task_execution)

    result = store.get_task_execution(task_execution.id)

    assert result is task_execution

def test_save_task_execution():
    store = InMemoryTaskStore()

    task_execution = TestTaskExecution(
        task_id=uuid4(),
        context=object(),
    )
    
    print(task_execution.id)

    store.save_task_execution(task_execution)

    result = store.get_task_execution(task_execution.id)

    assert result is task_execution
    assert result.id is not None
    assert result.id == task_execution.id
    assert result.task_id == task_execution.task_id
    assert result.started_at is None
    assert result.finished_at is None
    assert result.status == TaskExecutionStatus.PENDING
    assert result.context is task_execution.context



def test_get_unknown_task_execution_returns_none():
    store = InMemoryTaskStore()

    result = store.get_task_execution(uuid4())

    assert result is None

def test_list_task_executions():
    task_id1 = uuid4()
    task_id2 = uuid4()

    task_execution1 = TestTaskExecution(
        task_id=task_id1,
        context=object(),
    )
    task_execution2 = TestTaskExecution(
        task_id=task_id2,
        context=object(),
    )
    task_execution3 = TestTaskExecution(
        task_id=task_id1,
        context=object(),
    )

    store = InMemoryTaskStore()

    store.save_task_execution(task_execution1)
    store.save_task_execution(task_execution2)
    store.save_task_execution(task_execution3)

    result = store.list_task_executions(task_id1)

    assert len(result) == 2

    resutl_ids = {task_execution.id for task_execution in result}

    assert resutl_ids == {
        task_execution1.id,
        task_execution3.id
    }
    