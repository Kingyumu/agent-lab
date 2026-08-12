"""全局配置：从环境变量 / .env 加载。"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    agent_lab_host: str = "127.0.0.1"
    agent_lab_port: int = 8000
    log_level: str = "INFO"

    @property
    def has_api_key(self) -> bool:
        return bool(self.openai_api_key) and not self.openai_api_key.startswith("sk-your")


settings = Settings()
