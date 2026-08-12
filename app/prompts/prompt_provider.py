from pathlib import Path

class PromptProvider:

    def __init__(self, prompt_directory: Path):
        self.prompt_directory = prompt_directory

    def get(self, name: str):
        path = self.prompt_directory / f"{name}.txt"
        return path.read_text(encoding="utf-8")