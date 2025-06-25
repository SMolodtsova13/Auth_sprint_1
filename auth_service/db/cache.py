from abc import ABC, abstractmethod


class CacheStorage(ABC):

    @abstractmethod
    def get(*args, **kwargs):
        pass

    @abstractmethod
    def set(*args, **kwargs):
        pass

    @abstractmethod
    def delete(*args, **kwargs):
        pass

    @abstractmethod
    def close(*args, **kwargs):
        pass


cache_storage: CacheStorage | None = None


async def get_cache_storage() -> CacheStorage:
    return cache_storage
