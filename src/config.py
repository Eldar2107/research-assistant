from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    anthropic_api_key: str | None = None
    web_search_provider: str = "tavily"
    tavily_api_key: str | None = None
    cache_dir: str = "./.cache"
    cache_ttl_seconds: int = 86400

    class Config:
        env_file = ".env"

settings = Settings()