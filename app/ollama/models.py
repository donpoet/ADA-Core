from pydantic import BaseModel

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