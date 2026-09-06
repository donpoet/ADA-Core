from app.application.returns.context.task_execution_completed_return_context_source_factory import TaskExecutionCompletedReturnContextSourceFactory
from app.application.tasks.stores.memory_store import InMemoryTaskStore
from app.application.tasks.task_results.stores.memory_store import InMemoryTaskResultStore
from app.application.artifacts.stores.artifact_memory_store import InMemoryArtifactStore
from app.tasks.models import Task, TaskResult, TaskExecution
from uuid import uuid4
from app.tasks.enums import TaskType, TaskResultStatus
from app.artifacts.models import Artifact
from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.events.models import TaskExecutionCompletedEvent
from app.application.conversations.stores.memory_store import InMemoryConversationStore

class TestTaskExecution(TaskExecution):
    async def execute(self):
        pass

def test_create_return_context_source():
    # Create in-memory stores
    task_store = InMemoryTaskStore()
    task_result_store = InMemoryTaskResultStore()
    artifact_store = InMemoryArtifactStore()
    conversation_store = InMemoryConversationStore()

    conversation = conversation_store.create()

    # Create a task, task result, and artifacts
    task = Task(
        type=TaskType.HOME_AUTOMATION,
        conversation_id=conversation.id,
    )
    task_execution = TestTaskExecution(
        task_id=task.id,
        context=None,
        artifact_store=artifact_store
    )
    task_result = TaskResult(
        task_execution_id=task_execution.id,
        status=TaskResultStatus.SUCCESS,
        error_code=None
    )
    artifacts = [Artifact(
        artifact_type=ArtifactType.FILE,
        operation=ArtifactOperation.CREATE,
        reference="./artifact1.txt",
        task_execution_id=task_execution.id
    )]

    # Save them in the respective stores
    task_store.save_task(task)
    task_result_store.save_task_result(task_result)
    for artifact in artifacts:
        artifact_store.save_artifact(artifact)

    # Create the factory
    factory = TaskExecutionCompletedReturnContextSourceFactory(
        task_store=task_store,
        task_result_store=task_result_store,
        artifact_store=artifact_store,
        conversation_store=conversation_store
    )

    # Create an event
    event = TaskExecutionCompletedEvent(task_id=task.id, task_execution_id=task_execution.id, task_result_id=task_result.id)

    # Use the factory to create a ReturnContextSource
    return_context_source = factory.create(event)

    # Assertions to verify the correctness of the created ReturnContextSource
    assert return_context_source.task == task
    assert return_context_source.task_result == task_result
    assert return_context_source.artifacts == artifacts
    assert return_context_source.conversation == conversation

def test_create_return_context_source_with_no_artifacts():
    # Create in-memory stores
    task_store = InMemoryTaskStore()
    task_result_store = InMemoryTaskResultStore()
    artifact_store = InMemoryArtifactStore()
    conversation_store = InMemoryConversationStore()

    conversation = conversation_store.create()

    # Create a task, task result, and artifacts
    task = Task(
        type=TaskType.HOME_AUTOMATION,
        conversation_id=conversation.id,
    )
    task_execution = TestTaskExecution(
        task_id=task.id,
        context=None,
        artifact_store=artifact_store
    )
    task_result = TaskResult(
        task_execution_id=task_execution.id,
        status=TaskResultStatus.SUCCESS,
        error_code=None
    )

    # Save them in the respective stores
    task_store.save_task(task)
    task_result_store.save_task_result(task_result)

    # Create the factory
    factory = TaskExecutionCompletedReturnContextSourceFactory(
        task_store=task_store,
        task_result_store=task_result_store,
        artifact_store=artifact_store,
        conversation_store=conversation_store
    )

    # Create an event
    event = TaskExecutionCompletedEvent(task_id=task.id, task_execution_id=task_execution.id, task_result_id=task_result.id)

    # Use the factory to create a ReturnContextSource
    return_context_source = factory.create(event)

    # Assertions to verify the correctness of the created ReturnContextSource
    assert return_context_source.task == task
    assert return_context_source.task_result == task_result
    assert return_context_source.artifacts == []
    assert return_context_source.conversation == conversation