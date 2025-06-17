from fastapi import FastAPI

from api.v1 import auth
from db import redis_db, postgres


app = FastAPI(
    # title=settings.project_name,
    # docs_url='/api/openapi',
    # openapi_url='/api/openapi.json',
    # default_response_class=ORJSONResponse,
    # lifespan=lifespan
)


# Инициализация БД и Redis
@app.on_event('startup')
async def startup():
    redis_db.redis = redis_db.Redis(
        host='localhost', port=6379, db=0, decode_responses=True
    )
    from src.models.user import User
    await postgres.create_database()

@app.on_event('shutdown')
async def shutdown():
    await redis_db.redis.close()


app.include_router(auth.router, prefix='/auth', tags=['auth'])
