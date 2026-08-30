from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus
from uuid import uuid4, UUID
from datetime import (
    datetime,
    UTC,
    timedelta
)
from unittest.mock import AsyncMock

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

def test_filter_tasks_one_filter():
    task_store = InMemoryTaskStore()

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

def test_filter_tasks_multiple_filters():
    task_store = InMemoryTaskStore()

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

def test_filter_tasks_with_datetime_filter():
    task_store = InMemoryTaskStore()

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

def test_filter_tasks_no_filters():
    task_store = InMemoryTaskStore()

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

def test_filter_tasks_no_result():
    task_store = InMemoryTaskStore()

    result = task_store.filter_tasks(conversation_id=uuid4())
    
    assert result == []



def test_create_and_get_task_execution():
    store = InMemoryTaskStore()
    artifact_store = AsyncMock()

    task_execution = TestTaskExecution(
        task_id=uuid4(),
        context=object(),
        artifact_store=artifact_store
    )

    store.save_task_execution(task_execution)

    result = store.get_task_execution(task_execution.id)

    assert result is task_execution

def test_save_task_execution():
    store = InMemoryTaskStore()
    artifact_store = AsyncMock()

    task_execution = TestTaskExecution(
        task_id=uuid4(),
        context=object(),
        artifact_store=artifact_store
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

    artifact_store = AsyncMock()

    task_execution1 = TestTaskExecution(
        task_id=task_id1,
        context=object(),
        artifact_store=artifact_store
    )
    task_execution2 = TestTaskExecution(
        task_id=task_id2,
        context=object(),
        artifact_store=artifact_store
    )
    task_execution3 = TestTaskExecution(
        task_id=task_id1,
        context=object(),
        artifact_store=artifact_store
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
    