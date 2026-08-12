from app.prompts.prompt_provider import PromptProvider
from pathlib import Path

def test_prompt_provider_get():
    prompt_provider = PromptProvider(Path("tests/prompts"))

    result = prompt_provider.get("system")

    assert result == "test"