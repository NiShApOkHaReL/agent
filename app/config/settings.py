from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    search_limit: int = 20
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.5
    google_api_key: Optional[str]  
    serper_api_key: Optional[str]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
