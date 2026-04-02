from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_SECRET_KEY: str = "hackathon_secret_123"
    # Keep optional to avoid import-time crashes on hosts where env vars
    # are not set yet (e.g., first Vercel deploy). AI calls will still fail
    # at runtime until a valid key is provided.
    GEMINI_API_KEY: str = ""
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
