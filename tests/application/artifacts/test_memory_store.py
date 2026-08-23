from app.application.artifacts.stores.artifact_memory_store import InMemoryArtifactStore
from app.artifacts.models import Artifact
from app.artifacts.enums import ArtifactOperation, ArtifactType

from uuid import uuid4

def test_create_and_get_artifact():
    store = InMemoryArtifactStore()

    task_execution_id = uuid4()

    artifact = store.create_artifact(
            artifact_type=ArtifactType.LLM_RESPONSE,
            artifact_operation=ArtifactOperation.CREATE,
            task_execution_id=task_execution_id,
            reference=None,
            data=None
        )

    result = store.get_artifact(artifact.id)

    assert result is artifact
    assert result.id is not None
    assert result.artifact_type == artifact.artifact_type
    assert result.operation == artifact.operation
    assert result.reference is None
    assert result.task_execution_id is task_execution_id
    assert result.data is None

def test_save_artifact():
    store = InMemoryArtifactStore()

    task_execution_id = uuid4()

    artifact = store.create_artifact(
            artifact_type=ArtifactType.LLM_RESPONSE,
            artifact_operation=ArtifactOperation.CREATE,
            task_execution_id=task_execution_id,
            reference=None,
            data=None
        )

    artifact.reference = "some reference"
    
    store.save_artifact(artifact)

    result = store.get_artifact(artifact.id)

    assert result is artifact
    assert result.id is not None
    assert result.artifact_type == artifact.artifact_type
    assert result.operation == artifact.operation
    assert result.reference == "some reference"
    assert result.task_execution_id is task_execution_id
    assert result.data is None



def test_get_unknown_artifact_returns_none():
    store = InMemoryArtifactStore()

    result = store.get_artifact(uuid4())

    assert result is None

def test_list_artifacts():
    store = InMemoryArtifactStore()
    
    task_execution_id1 = uuid4()
    task_execution_id2 = uuid4()

    artifact1 = store.create_artifact(
            artifact_type=ArtifactType.LLM_RESPONSE,
            artifact_operation=ArtifactOperation.CREATE,
            task_execution_id=task_execution_id1,
            reference=None,
            data=None
        )
    artifact2 = store.create_artifact(
            artifact_type=ArtifactType.LLM_RESPONSE,
            artifact_operation=ArtifactOperation.CREATE,
            task_execution_id=task_execution_id2,
            reference=None,
            data=None
        )
    artifact3 = store.create_artifact(
            artifact_type=ArtifactType.LLM_RESPONSE,
            artifact_operation=ArtifactOperation.CREATE,
            task_execution_id=task_execution_id1,
            reference=None,
            data=None
        )

    store.save_artifact(artifact1)
    store.save_artifact(artifact2)
    store.save_artifact(artifact3)

    result = store.list_artifacts(task_execution_id1)

    assert len(result) == 2

    resutl_ids = {artifact.id for artifact in result}

    assert resutl_ids == {
        artifact1.id,
        artifact3.id
    }