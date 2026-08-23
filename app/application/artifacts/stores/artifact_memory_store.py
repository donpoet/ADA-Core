from app.artifacts.enums import ArtifactOperation, ArtifactType
from app.artifacts.models import Artifact
from .artifact_store import ArtifactStore

from uuid import UUID, uuid4

class InMemoryArtifactStore(ArtifactStore):

    def __init__(self):
        self._artifacts : dict[UUID, Artifact] = {}

        
    def create_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_operation: ArtifactOperation,
        task_execution_id: UUID,
        reference: str | None = None,
        data: dict | None = None
        ) -> Artifact:
        artifact = Artifact(
            artifact_type=artifact_type,
            operation=artifact_operation,
            reference=reference,
            task_execution_id=task_execution_id,
            data=data
        )

        self._artifacts[artifact.id] = artifact
        return artifact

    
    def get_artifact(self, artifact_id: UUID) -> Artifact:
        return self._artifacts.get(artifact_id)

    
    def save_artifact(self, artifact: Artifact) -> None:
        self._artifacts[artifact.id] = artifact


    def list_artifacts(self, execution_id: UUID) -> list[Artifact]:
        artifacts = []
        for artifact in self._artifacts.values():
            if artifact.task_execution_id == execution_id:
                artifacts.append(artifact)

        return artifacts
