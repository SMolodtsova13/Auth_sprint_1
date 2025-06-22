from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, roles
from db import redis_db, postgres
from api.v1 import access_token


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


# Подключение роутера авторизации
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(roles.router, prefix='/api/v1')
