"""Processor service configuration."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    service_name: str = "processor"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "alert-processor"
    redis_url: str = "redis://localhost:6379/0"
    dedup_window_seconds: int = 300
    converge_window_seconds: int = 300
    converge_max_count: int = 100


settings = Settings()
