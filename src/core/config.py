import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProxyConfig:
    url: str
    username: Optional[str] = None
    password: Optional[str] = None


class Settings:
    def __init__(self):
        # BOT
        self.BOT_TOKEN = self._get_env("BOT_TOKEN", required=True)

        # PROXY
        self.USE_PROXY = self._get_env("USE_PROXY", "false").lower() == "true"
        self.PROXY: Optional[ProxyConfig] = (
            self._get_proxy_config() if self.USE_PROXY else None
        )

        # DATABASE
        self.DB_USER = self._get_env(
            "POSTGRES_USER", "postgres"
        )  # Default for safety, normally required
        self.DB_PASS = self._get_env("POSTGRES_PASSWORD", "postgres")
        self.DB_HOST = self._get_env("POSTGRES_HOST", "localhost")
        self.DB_PORT = self._get_env("POSTGRES_PORT", "5432")
        self.DB_NAME = self._get_env("POSTGRES_DB", "postgres")

    def _get_env(
        self, key: str, default: Optional[str] = None, required: bool = False
    ) -> str:
        value = os.environ.get(key, default)
        if required and value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    def _get_proxy_config(self) -> ProxyConfig:
        return ProxyConfig(
            url=self._get_env("PROXY_URL", required=True),
            username=self._get_env("USERNAME"),
            password=self._get_env("PASSWORD"),
        )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
