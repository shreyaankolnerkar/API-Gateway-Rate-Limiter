from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres.rciroqsqrkttqghfkrso:Shreya29399@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    )
    REDIS_URL: str = "redis://api-gateway-redis:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
