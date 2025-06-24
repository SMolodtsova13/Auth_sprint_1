from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.openapi.utils import get_openapi

from api.urls import router
from db import redis_db


app = FastAPI(
    title='Auth Service',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

# Кастомизация OpenAPI для Bearer Token авторизации
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title='Auth Service',
        version='1.0.0',
        description='Документация авторизации',
        routes=app.routes,
    )
    # Определяем OAuth2 схему с tokenUrl и refreshUrl
    openapi_schema.setdefault('components', {})['securitySchemes'] = {
        'OAuth2PasswordBearer': {
            'type': 'oauth2',
            'flows': {
                'password': {
                    'tokenUrl': '/api/v1/auth/login',
                    'refreshUrl': '/api/v1/auth/refresh',
                    'scopes': {},
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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
