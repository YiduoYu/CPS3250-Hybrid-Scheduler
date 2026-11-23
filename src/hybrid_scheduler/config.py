from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Central project configuration loaded from environment variables or .env file."""

    # --- App basics ---------------------------------------------------------
    app_name: str = Field("Hybrid Scheduler", env="APP_NAME")
    environment: str = Field("dev", env="ENVIRONMENT")  # dev | prod | test

    # --- Server settings ----------------------------------------------------
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8080, env="PORT")

    # --- RabbitMQ -----------------------------------------------------------
    rabbitmq_url: str = Field(
        "amqp://guest:guest@localhost:5672/", env="RABBITMQ_URL"
    )

    # --- AWS credentials & region ------------------------------------------
    aws_region: str = Field("us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")

    # --- Prometheus ---------------------------------------------------------
    prom_port: int = Field(8000, env="PROM_PORT")

    class Config:
        # automatically load "../.env" if present
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance so expensive disk IO happens once."""

    return Settings()