from sqlalchemy.orm import Session
from .artifact_store import ArtifactStore

from app.artifacts.models import Artifact
from app.artifacts.enums import ArtifactOperation, ArtifactType

from app.database.schema import ArtifactModel, TaskExecutionModel

from uuid import UUID

class SQLiteArtifactStore(ArtifactStore):

    def __init__(self, engine):
        self._engine = engine

    def create_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_operation: ArtifactOperation,
        task_execution_id: UUID,
        reference: str | None = None,
        data: dict | None = None,
    ) -> Artifact:

        artifact = Artifact(
            artifact_type=artifact_type,
            operation=artifact_operation,
            reference=reference,
            task_execution_id=task_execution_id,
            data=data
        )

        with Session(self._engine) as session:
            session.add(
                ArtifactModel(
                    id=str(artifact.id),
                    artifact_type=artifact.artifact_type,
                    operation=artifact.operation,
                    reference=artifact.reference,
                    task_execution_id=str(artifact.task_execution_id),
                    data=artifact.data
                )
            )
            session.commit()

        return artifact

    def get_artifact(self, artifact_id: UUID) -> Artifact:
        with Session(self._engine) as session:
            artifact_model = session.get(
                ArtifactModel,
                str(artifact_id),
            )

            if artifact_model is None:
                raise ValueError(
                    f"Artifact {artifact_id} not found"
                )
            
            return Artifact(
                id=UUID(artifact_model.id),
                artifact_type=artifact_model.artifact_type,
                operation=artifact_model.operation,
                reference=artifact_model.reference,
                task_execution_id=UUID(artifact_model.task_execution_id),
                data=artifact_model.data,
            )

    def save_artifact(self, artifact: Artifact) -> None:
        with Session(self._engine) as session:
            artifact_model = session.get(
                ArtifactModel,
                str(artifact.id)
            )

            if artifact_model is None:
                artifact_model = ArtifactModel(
                    id=str(artifact.id),
                    artifact_type=artifact.artifact_type,
                    operation=artifact.operation,
                    reference=artifact.reference,
                    task_execution_id=artifact.task_execution_id,
                    data=artifact.data
                )
                session.add(artifact_model)    
            
            artifact_model.artifact_type=artifact.artifact_type
            artifact_model.operation=artifact.operation
            artifact_model.reference=artifact.reference
            artifact_model.task_execution_id=str(artifact.task_execution_id)
            artifact_model.data=artifact.data

            session.commit()

    def list_artifacts(self, execution_id: UUID) -> list[Artifact]:
        artifacts: list[Artifact] = []
        with Session(self._engine) as session:
            task_execution_model = session.get(
                TaskExecutionModel,
                str(execution_id)
            )

            if task_execution_model is None:
                raise ValueError(
                    f"TaskExecution {execution_id} not found"
                )
            
            for artifact_model in task_execution_model.artifacts:
                artifacts.append( 
                    Artifact(
                        id=UUID(artifact_model.id),
                        artifact_type=artifact_model.artifact_type,
                        operation=artifact_model.operation,
                        reference=artifact_model.reference,
                        task_execution_id=UUID(artifact_model.task_execution_id),
                        data=artifact_model.data,
                    )
                )

        return artifacts

            
