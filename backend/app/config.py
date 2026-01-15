"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_interviewer"

    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week
    
    # Uppercase aliases for compatibility
    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key
    
    @property
    def ALGORITHM(self) -> str:
        return self.algorithm

    # LLM Provider
    llm_provider: str = "openai"  # openai, gemini, ollama
    llm_model: str = "gpt-4"
    openai_api_key: str | None = None
    google_api_key: str | None = None

    # File Storage
    upload_dir: str = "./uploads"

    # Interview Configuration
    default_target_questions: int = 8
    default_difficulty_start: int = 5

    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    cache_max_size: int = 1000

    # Cost tracking
    cost_tracking_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
