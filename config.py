from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-4-turbo-preview"
    max_tokens: int = 1000
    temperature: float = 0.7

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
