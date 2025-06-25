from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.urls import router
from db import redis_db


app = FastAPI(
    title='Auth Service',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

@app.on_event('startup')
async def startup():
    """Инициализация Redis при старте приложения."""
    redis_db.redis = redis_db.Redis(
        host='redis', port=6379, db=0, decode_responses=True
    )


@app.on_event('shutdown')
async def shutdown():
    """
    Закрытие соединения с Redis при завершении работы приложения.
    """
    await redis_db.redis.close()


app.include_router(router)
