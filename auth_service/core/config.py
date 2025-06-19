from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # PostgreSQL
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'auth_db'

    # Redis
    redis_host: str
    redis_port: int
    redis_db: int = 0

    # JWT
    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    class Config:
        env_file = '.env'

    @property
    def pg_url(self):
        return (
            'postgresql+asyncpg://'
            f'{settings.postgres_user}:{settings.postgres_password}@'
            f'{settings.postgres_host}:{settings.postgres_port}/'
            f'{settings.postgres_db}'
        )


settings = Settings()
