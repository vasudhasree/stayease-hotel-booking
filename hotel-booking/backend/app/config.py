from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "stayease-development-secret-change-me"
    DATABASE_URL: str = "sqlite:///./hotel.db"
    CORS_ORIGINS: str = "http://localhost:5173"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
