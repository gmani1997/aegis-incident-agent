import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-flash-latest"
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO: Optional[str] = None
    MOCK_GITHUB: bool = True
    MAX_REPAIR_ATTEMPTS: int = 3
    DEFAULT_TARGET_REPO_PATH: str = "./sandbox/broken_service"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
