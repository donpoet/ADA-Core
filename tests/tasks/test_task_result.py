from app.tasks.models import TaskResult, TaskResultStatus

from uuid import uuid4

def test_task_result_creation():
    task_result = TaskResult(
        task_execution_id=uuid4(),
        status=TaskResultStatus.SUCCESS,
        error_code=None
    )

    assert task_result.id is not None
    assert task_result.status == TaskResultStatus.SUCCESS
    assert task_result.error_code is None
    assert task_result.task_execution_id is not None