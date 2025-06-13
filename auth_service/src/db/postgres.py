from core.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


# Создаём базовый класс для будущих моделей
Base = declarative_base()
# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
dsn = f'postgresql+asyncpg://{settings.user}:{settings.password}@{settings.host}:{settings.port}/{settings.db}'
engine = create_async_engine(dsn, echo=True, future=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Создание/удаление таблиц
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
