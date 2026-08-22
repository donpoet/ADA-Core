from app.tasks.models import Task, InvalidTaskStateError
from app.tasks.enums import TaskStatus, TaskType

from uuid import uuid4
import pytest

def test_task_creation():
    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM
    )

    assert task.conversation_id is not None
    assert task.status == TaskStatus.OPEN
    assert task.created_at is not None
    assert task.id is not None
    assert task.completed_at is None 
    assert task.source_message_ids == []

def test_task_workflow():
    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM
    )

    task.complete()

    assert task.status == TaskStatus.COMPLETED
    assert task.completed_at is not None

    with pytest.raises(InvalidTaskStateError):
        task.complete()

    with pytest.raises(InvalidTaskStateError):
        task.cancel()

    task = Task(
        conversation_id=uuid4(),
        type=TaskType.WEAK_LLM
    )

    task.cancel()

    assert task.status == TaskStatus.CANCELLED
    assert task.completed_at is None