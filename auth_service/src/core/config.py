from pydantic import BaseSettings


class Settings(BaseSettings):
    user: str = 'postgres'
    password: str = 'postgres'
    host: str = 'localhost'
    port: int = 5432
    db: str = 'auth_db'

    class Config:
        env_file = '.env'

settings = Settings()
