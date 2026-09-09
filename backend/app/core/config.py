import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./reviewagentai.db",
    )

    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173",
    )

    groq_api_key: str | None = os.getenv("GROQ_API_KEY")

    groq_model: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
