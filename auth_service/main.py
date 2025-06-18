from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth
from db import redis_db, postgres



app = FastAPI(
    # title=settings.project_name,
    title='Auth Service',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    # lifespan=lifespan
)


@app.on_event('startup')
async def startup():
    redis_db.redis = redis_db.Redis(
        host='localhost', port=6379, db=0, decode_responses=True
    )
    """Инициализация Redis при старте приложения."""
    await postgres.create_database()


@app.on_event('shutdown')
async def shutdown():
    """
    Закрытие соединения с Redis при завершении работы приложения.
    """
    await redis_db.redis.close()


# Подключение роутера авторизации
app.include_router(auth.router, prefix='/auth', tags=['auth'])
