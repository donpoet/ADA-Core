from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.artifacts.models import Artifact

from uuid import uuid4

def test_artifact_creation():
    task_execution_id = uuid4()

    artifact = Artifact(
        artifact_type=ArtifactType.LLM_RESPONSE,
        operation=ArtifactOperation.CREATE,
        reference=None,
        task_execution_id=task_execution_id,
        data=None,
    )

    assert artifact.id is not None
    assert artifact.artifact_type == ArtifactType.LLM_RESPONSE
    assert artifact.operation == ArtifactOperation.CREATE
    assert artifact.task_execution_id is task_execution_id
    assert artifact.reference is None
    assert artifact.data is None