__version__ = "0.0.1"


__desription__ = f"""
Version {__version__}:
"""

from pathlib import Path
from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_PROJECT_DIR = Path(__file__).parents[3]


class Environment(Enum):
    DEV = "dev"
    PROD = "prod"
    QA = "qa"


class Settings(BaseSettings):
    ENV: Environment = Environment.DEV
    LOG_LEVEL: str = "DEBUG"

    BOT_TOKEN: str
    BOT_NAME: str = "Sunlight_Randomaizer_Bot"
    BOT_WEBAPP_NAME: str = "webapp"

    IMG_FOLDER: str = str(ROOT_PROJECT_DIR / "static")

    SQLITE_DB_URI: str = str(ROOT_PROJECT_DIR / "db" / "sl_db.sqlite")
    REDIS_BROKER_URI: str = "redis://localhost:6379/11"
    REDIS_BROKER_RESULT_BACKEND_URI: str = "redis://localhost:6379/12"

    PERIODIC_TASKS_TIMEOUT_SECONDS: int = 10

    API_PORT: int = 8000
    API_RELOAD: bool = False

    ROOT_ADMIN_TG_IDS: list[int]
    # ROOT_ADMIN_PHONES: list[int]

    model_config = SettingsConfigDict(
        env_file=ROOT_PROJECT_DIR/".env",
    )


SETTINGS = Settings()  # type:ignore
