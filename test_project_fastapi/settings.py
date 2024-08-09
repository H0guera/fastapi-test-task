import os
import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Iterable

from pydantic_settings import BaseSettings, SettingsConfigDict

from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "test_project_fastapi"
    db_pass: str = "test_project_fastapi"
    db_base: str = "admin"
    db_echo: bool = False

    # Variables for count of active performers
    performers: int = 2

    # Variable for time offset
    time_offset: int = 3

    # Variables for room numbers
    first_room_number: int = 1
    last_room_number: int = 200

    @property
    def available_room_numbers(self) -> Iterable[int]:
        """
        Generate range of ints of available room numbers.

        :return: Range of ints of available room numbers.
        """
        return range(self.first_room_number, self.last_room_number + 1)

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TEST_PROJECT_FASTAPI_",
        env_file_encoding="utf-8",
    )


settings = Settings()
