from pydantic_settings import BaseSettings


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
            f'{settings.pg_user}:{settings.pg_password}@'
            f'{settings.pg_host}:{settings.pg_port}/'
            f'{settings.pg_db}'
        )

settings = Settings()
