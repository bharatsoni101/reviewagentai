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
        "openai/gpt-oss-120b",
    )

    review_session_timeout_minutes: int = int(os.getenv("REVIEW_SESSION_TIMEOUT_MINUTES", "30"))
    ai_rate_limit_requests: int = int(os.getenv("AI_RATE_LIMIT_REQUESTS", "10"))
    ai_rate_limit_window_seconds: int = int(os.getenv("AI_RATE_LIMIT_WINDOW_SECONDS", "60"))
    private_feedback_rate_limit_requests: int = int(os.getenv("PRIVATE_FEEDBACK_RATE_LIMIT_REQUESTS", "5"))
    private_feedback_rate_limit_window_seconds: int = int(os.getenv("PRIVATE_FEEDBACK_RATE_LIMIT_WINDOW_SECONDS", "60"))
    business_api_key: str | None = os.getenv("BUSINESS_API_KEY")

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
