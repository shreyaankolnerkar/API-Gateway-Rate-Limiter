from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres.rciroqsqrkttqghfkrso:Shreya29399@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    )

    class Config:
        env_file = ".env"


settings = Settings()
