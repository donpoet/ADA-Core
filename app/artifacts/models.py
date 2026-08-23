from .enums import ArtifactOperation, ArtifactType
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Artifact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    artifact_type: ArtifactType
    operation: ArtifactOperation
    reference: str | None = None
    task_execution_id: UUID
    data: dict | None = None