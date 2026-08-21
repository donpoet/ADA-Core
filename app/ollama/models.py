from pydantic import BaseModel

from app.context.models import ContextSource, ContextOutput
from app.conversation.models import Conversation
from app.llm_models.models import ModelOutput

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaResponse(BaseModel):
    model: str
    response: str
    done: bool

    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None

class OllamaChatResponse(BaseModel):
    model: str
    message: OllamaMessage
    done: bool

    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None

class OllamaContextSource(ContextSource, BaseModel):
    conversation: Conversation

class OllamaContextOutput(ContextOutput, BaseModel):
    messages: list[dict[str, str]]

class OllamaModelOutput(ModelOutput, BaseModel):
    content: str