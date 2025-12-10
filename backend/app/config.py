from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Ruta base del proyecto backend
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Backend API"
    debug: bool = True
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/app.db"

    # JWT Configuration
    secret_key: str = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
