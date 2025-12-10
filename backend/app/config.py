"""
Configuración de la aplicación usando variables de entorno.

Este módulo carga las configuraciones desde variables de entorno
definidas en el archivo .env ubicado en el directorio backend/.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List

# Ruta base del proyecto backend
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Todas las variables se cargan desde el archivo .env.
    Los valores por defecto se usan solo si no hay .env.
    """

    # ===========================================
    # INFORMACIÓN DE LA APLICACIÓN
    # ===========================================
    app_name: str = "Marco Habit Tracker"
    api_version: str = "2.0.0"
    api_description: str = "API para seguimiento de hábitos con autenticación JWT"

    # ===========================================
    # ENTORNO Y DEBUG
    # ===========================================
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ===========================================
    # SERVIDOR
    # ===========================================
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

    # ===========================================
    # BASE DE DATOS
    # ===========================================
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/app.db"

    # ===========================================
    # SEGURIDAD - JWT
    # ===========================================
    secret_key: str = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 días

    # ===========================================
    # CORS - Orígenes Permitidos
    # ===========================================
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte la cadena de orígenes CORS en una lista."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Retorna True si está en modo producción."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Retorna True si está en modo desarrollo."""
        return self.environment.lower() == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia cacheada de Settings.

    El decorador @lru_cache asegura que solo se cree
    una instancia de Settings durante toda la ejecución.
    """
    return Settings()
