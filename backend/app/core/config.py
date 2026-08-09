from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pulse AI Interview Agent"
    VERSION: str = "0.1.0"

    # Application Configuration
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/pulse_ai_db"

    # Gemini LLM Settings
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()