from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConn(BaseModel):
    """Базовый класс подключения."""

    host: str
    port: int


class Redis(BaseConn):
    """Настройки Redis."""

    pass


class TestSettings(BaseSettings):
    """Настройки проекта."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='_'
    )

    redis: Redis
    service_url: str = 'http://api:8000'


test_settings = TestSettings()
