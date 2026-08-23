from abc import ABC, abstractmethod
from uuid import UUID

from app.artifacts.models import Artifact
from app.artifacts.enums import ArtifactOperation, ArtifactType

class ArtifactStore(ABC):

    @abstractmethod
    def create_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_operation: ArtifactOperation,
        task_execution_id: UUID,
        reference: str | None = None,
        data: dict | None = None
        ) -> Artifact:
        pass

    @abstractmethod
    def get_artifact(self, artifact_id: UUID) -> Artifact:
        pass

    @abstractmethod
    def save_artifact(self, artifact: Artifact) -> None:
        pass

    @abstractmethod
    def list_artifacts(self, execution_id: UUID) -> list[Artifact]:
        pass
