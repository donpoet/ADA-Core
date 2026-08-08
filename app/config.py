from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_url: str = "http://ada:11434"
    ollama_timeout: int = 300
    default_model: str = "qwen3:4b"

    class Config:
        env_file = ".env"

settings = Settings()