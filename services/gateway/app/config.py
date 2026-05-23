"""Gateway service configuration."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    service_name: str = "gateway"
    debug: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    rate_limit_per_minute: int = 1000


settings = Settings()
