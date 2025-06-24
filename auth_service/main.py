from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.urls import router
from core.config import settings
from db import cache


async def init_redis():
    redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    await redis_client.ping()
    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Подключение к БД при старте сервера и отключение при остановке."""
    cache.cache_storage = await init_redis()
    yield
    await cache.cache_storage.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(router)
