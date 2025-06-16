from core.config import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
# dsn = f'postgresql+asyncpg://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.db}'
dsn = (
    f'postgresql+asyncpg://'
    f'{settings.pg_user}:{settings.pg_password}@'
    f'{settings.pg_host}:{settings.pg_port}/'
    f'{settings.pg_db}'
)
engine = create_async_engine(dsn, echo=True, future=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# DI-зависимость для FastAPI
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Создание/удаление таблиц
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
