from pydantic import BaseModel

class OllamaResponse(BaseModel):
    model: str
    response: str
    done: bool

    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None