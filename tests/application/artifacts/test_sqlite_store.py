from sqlalchemy.orm import Session

from app.application.tasks.stores.sqlite_store import SQLiteTaskStore
from app.application.conversations.stores.sqlite_store import SQLiteConversationStore
from app.conversation.models import Message, MessageRole
from app.database.schema import ArtifactModel

from app.tasks.models import Task, TaskExecution
from app.tasks.enums import TaskType, TaskStatus, TaskExecutionStatus
from app.artifacts.models import Artifact
from app.artifacts.enums import ArtifactOperation, ArtifactType

from app.application.artifacts.stores.artifact_sqlite_store import SQLiteArtifactStore

from app.ollama.models import OllamaContextOutput

from app.dependencies import task_component_registry

from datetime import datetime, UTC
from uuid import uuid4, UUID

import pytest
from unittest.mock import AsyncMock

def test_create_artifact(db_engine):
    store = SQLiteArtifactStore(db_engine)
    task_execution_id = uuid4()

    artifact = store.create_artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        artifact_operation=ArtifactOperation.CREATE,
        task_execution_id=task_execution_id,
        reference=None,
        data={
            "content" : "Hallo Michael!"
        }
    )

    assert artifact.id is not None
    assert artifact.artifact_type is ArtifactType.LLM_RESPONSE
    assert artifact.operation is ArtifactOperation.CREATE
    assert artifact.task_execution_id == task_execution_id
    assert artifact.reference is None
    assert artifact.data == {
        "content": "Hallo Michael!"
    }

    with Session(db_engine) as session:
        stored = session.get(
            ArtifactModel,
            str(artifact.id)
        )

        assert stored is not None
        assert stored.id == str(artifact.id)
        assert stored.artifact_type == artifact.artifact_type
        assert stored.operation == artifact.operation
        assert stored.task_execution_id == str(artifact.task_execution_id)
        assert stored.reference == artifact.reference
        assert stored.data == artifact.data

def test_get_artifact(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_store.save_task_execution(execution)

    artifact = artifact_store.create_artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        artifact_operation=ArtifactOperation.CREATE,
        task_execution_id=execution.id,
        reference=None,
        data={
            "content" : "Hallo Michael!"
        }
    )

    result = artifact_store.get_artifact(artifact.id)

    assert isinstance(result, Artifact)
    assert result.id == artifact.id
    assert result.artifact_type == artifact.artifact_type
    assert result.operation == artifact.operation
    assert result.task_execution_id == artifact.task_execution_id
    assert result.reference == artifact.reference
    assert result.data == artifact.data

def test_get_unknown_artifact_raises_value_error(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)

    with pytest.raises(ValueError):
        artifact_store.get_artifact(uuid4())

def test_save_artifact(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_store.save_task_execution(execution)

    artifact = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        task_execution_id=execution.id,
        reference=None,
        data={
            "content" : "Hallo Michael!"
        }
    )

    artifact_store.save_artifact(artifact)

    result = artifact_store.get_artifact(artifact.id)

    assert isinstance(result, Artifact)
    assert result.id == artifact.id
    assert result.artifact_type == artifact.artifact_type
    assert result.operation == artifact.operation
    assert result.task_execution_id == artifact.task_execution_id
    assert result.reference == artifact.reference
    assert result.data == artifact.data

def test_save_artifact_with_modification(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    task_store.save_task_execution(execution)

    artifact = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        task_execution_id=execution.id,
        reference=None,
        data={
            "content" : "Hallo Michael!"
        }
    )

    artifact_store.save_artifact(artifact)

    artifact.artifact_type=ArtifactType.CALENDAR_ENTRY
    artifact.reference="./"
    artifact.data=None
    artifact.operation=ArtifactOperation.UPDATE

    artifact_store.save_artifact(artifact)

    result = artifact_store.get_artifact(artifact.id)

    assert isinstance(result, Artifact)
    assert result.id == artifact.id
    assert result.artifact_type == artifact.artifact_type
    assert result.operation == artifact.operation
    assert result.task_execution_id == artifact.task_execution_id
    assert result.reference == artifact.reference
    assert result.data == artifact.data

def test_list_artifacts(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    execution1 = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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
    execution2 = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
        task.id,
        OllamaContextOutput(
            messages=[
                {
                    "role": "user",
                    "content": "Wie geht's, Ada?"
                }
            ]
        )
    )
    task_store.save_task_execution(execution1)
    task_store.save_task_execution(execution2)

    artifact1 = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        task_execution_id=execution1.id,
        reference=None,
        data={
            "content" : "Hallo Michael!"
        }
    )

    artifact2 = Artifact(
        artifact_type=ArtifactType.DIRECTORY,
        operation=ArtifactOperation.CREATE,
        task_execution_id=execution1.id,
        reference="./",
        data=None
    )

    artifact3 = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        task_execution_id=execution2.id,
        reference=None,
        data={
            "content" : "Gut, und dir?"
        }
    )

    artifact_store.save_artifact(artifact1)
    artifact_store.save_artifact(artifact2)
    artifact_store.save_artifact(artifact3)

    expected_ids1 = [artifact1.id, artifact2.id]
    expected_ids2 = [artifact3.id]

    result1 = artifact_store.list_artifacts(execution1.id)
    result2 = artifact_store.list_artifacts(execution2.id)

    result_ids1 = [artifact.id for artifact in result1]
    result_ids2 = [artifact.id for artifact in result2]

    assert set(expected_ids1) == set(result_ids1)
    assert set(expected_ids2) == set(result_ids2)

def test_list_artifacts_raises_value_error_for_unknown_execution(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    
    with pytest.raises(ValueError):
        artifact_store.list_artifacts(uuid4())

def test_list_artifacts_returns_empty_list_for_execution_without_artifacts(db_engine):
    artifact_store = SQLiteArtifactStore(db_engine)
    conversation_store = SQLiteConversationStore(db_engine)
    task_store = SQLiteTaskStore(db_engine, task_component_registry)

    conversation = conversation_store.create()

    task = task_store.create_task(TaskType.WEAK_LLM, conversation.id)

    execution = task_component_registry.get(TaskType.WEAK_LLM).execution_factory.create(
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

    task_store.save_task_execution(execution)

    result = artifact_store.list_artifacts(execution.id)

    assert result == []
