from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_url: str = "http://ada:11434"
    ollama_timeout: int = 300
    default_model: str = "qwen3:4b"
    intent_model: str = "qwen3:4b"
    database_url: str = "sqlite:///data/adacore.db"
    default_model_thinking: bool = True
    default_model_options: dict = {"temperature": 0.5}    
    intent_model_thinking: bool = False
    intent_model_options: dict = {"temperature": 0}
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="ignore",
    )
        

settings = Settings()