from pydantic import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    pg_user: str = 'postgres'
    pg_password: str = 'postgres'
    pg_host: str = 'localhost'
    pg_port: int = 5432
    pg_db: str = 'auth_db'

    # Redis
    redis_host: str
    redis_port: int
    redis_db: int = 0

    class Config:
        env_file = '.env'

settings = Settings()

