import pytest
from uuid import uuid4

from app.tasks.models import Task, TaskExecution, InvalidTaskExecutionStateError
from app.tasks.enums import TaskType, TaskExecutionStatus, TaskResultStatus

class TestTaskExecution(TaskExecution[object]):
    def execute(self):
        pass

def test_task_execution_creation():
    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM,
    )

    task_execution = TestTaskExecution(
        task_id=task.id,
        context=[],
    )

    assert task_execution.id is not None
    assert task_execution.context == []
    assert task_execution.task_id == task.id
    assert task_execution.status == TaskExecutionStatus.PENDING
    assert task_execution.started_at is not None
    assert task_execution.finished_at is None

def test_task_execution_lifecycle():
    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM,
    )

    task_execution = TestTaskExecution(
        task_id=task.id,
        context=[],
    )

    task_execution.start()

    assert task_execution.status == TaskExecutionStatus.RUNNING
    assert task_execution.finished_at is None

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.start()
    
    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM,
    )

    task_execution = TestTaskExecution(
        task_id=task.id,
        context=[],
    )

    task_execution.start()
    task_execution.complete()

    assert task_execution.status == TaskExecutionStatus.COMPLETED
    assert task_execution.finished_at is not None

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.cancel()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.fail()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.complete()

    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM,
    )

    task_execution = TestTaskExecution(
        task_id=task.id,
        context=[],
    )

    task_execution.cancel()

    assert task_execution.status == TaskExecutionStatus.CANCELLED
    assert task_execution.finished_at is not None

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.cancel()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.fail()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.complete()

    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM,
    )

    task_execution = TestTaskExecution(
        task_id=task.id,
        context=[],
    )

    task_execution.start()
    task_execution.fail()

    assert task_execution.status == TaskExecutionStatus.FAILED
    assert task_execution.finished_at is not None

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.cancel()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.fail()

    with pytest.raises(InvalidTaskExecutionStateError):
        task_execution.complete()