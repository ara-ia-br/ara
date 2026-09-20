from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60



    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    OPENAI_MODEL: str = "gpt-5.6-sol"

    OPENAI_REASONING_EFFORT: str = "low"

    OPENAI_SERVICE_TIER: str = "fast"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3.5:4b"

    model_config = SettingsConfigDict(
        env_file="config.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


setting = Setting()
