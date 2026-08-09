from pydantic import (
    BaseModel,
    Field
)
from uuid import (
    uuid4,
    UUID,
)

class ChatServiceResponse(BaseModel):
    conversation_id: UUID = Field(default_factory=uuid4)
    content: str