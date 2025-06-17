from typing import Optional
from redis.asyncio import Redis
from core.config import settings

redis: Optional[Redis] = None

async def get_redis() -> Redis:
    return redis
