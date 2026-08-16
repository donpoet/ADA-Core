from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_url: str = "http://ada:11434"
    ollama_timeout: int = 300
    default_model: str = "qwen3:4b"
    database_url: str = "sqlite:///data/adacore.db"

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="ignore",
    )
        

settings = Settings()