import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    cache_dir: str = os.getenv("CACHE_DIR", "./.cache")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", 86400))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    per_source_timeout_seconds: int = int(os.getenv("PER_SOURCE_TIMEOUT_SECONDS", 10))  # <--- Bunu əlavə edirik

settings = Settings()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@research-postgres:5432/research_assistant')