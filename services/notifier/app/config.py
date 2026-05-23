"""Notifier service configuration."""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    service_name: str = "notifier"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "alert-notifier"
    max_retries: int = 3
    retry_delay_seconds: int = 5

settings = Settings()
