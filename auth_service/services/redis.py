import json
from abc import ABC, abstractmethod
from pydantic import BaseModel

from db.cache import CacheStorage


class AbstractCache(ABC):
    """Абстрактный класс для работы с временным хранилищем."""

    @abstractmethod
    async def get_from_cache(
        self,
        key: str,
        model: BaseModel
    ) -> BaseModel | list[BaseModel] | None:
        """Получение данных из временного хранилища."""
        pass

    @abstractmethod
    async def put_to_cache(
        self,
        key: str,
        obj: BaseModel | list[BaseModel],
        expire: int
    ) -> None:
        """Добавление данных во временное хранилище."""
        pass


class CacheService(AbstractCache):
    """Сервис для работы с временным хранилищем."""

    def __init__(self, cache_storage: CacheStorage):
        self.cache_storage = cache_storage

    async def get_from_cache(
        self,
        key: str,
        schema: BaseModel
    ) -> BaseModel | list[BaseModel] | None:
        """Получение объекта из временного хранилища."""
        data = await self.cache_storage.get(key)
        if data:
            return schema(**json.loads(data))

    async def put_to_cache(
        self,
        key: str,
        obj: BaseModel | list[BaseModel],
        expire: int
    ) -> None:
        """Добавление объекта во временное хранилище."""
        json_obj = obj.model_dump_json()
        await self.cache_storage.set(key, json_obj, expire)
