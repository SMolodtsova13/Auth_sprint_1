from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base


class AbstractDb(ABC):
    """Абстрактный класс для с БД."""

    @abstractmethod
    def get_by_id(*args, **kwargs):
        pass

    @abstractmethod
    def get_by_kwargs(*args, **kwargs):
        pass

    @abstractmethod
    def get_all(*args, **kwargs):
        pass

    @abstractmethod
    def create(*args, **kwargs):
        pass

    @abstractmethod
    def update(*args, **kwargs):
        pass

    @abstractmethod
    def delete(*args, **kwargs):
        pass


class DbService(AbstractDb):
    """Сервис работы с БД."""

    def __init__(self, db: AsyncSession, model: Base) -> None:
        self.db = db
        self.model = model

    async def get_by_id(self, id: UUID) -> Base | None:
        """Метод получения объекта модели по id."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_kwargs(self, **kwargs) -> list[Base]:
        """Метод получения объектов по переданным параметрам."""
        result = await self.db.execute(select(self.model).filter_by(**kwargs))
        return result.scalars().all()

    async def get_all(self) -> list[Base]:
        """Метод получения всех объектов модели из БД."""
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj: BaseModel) -> Base:
        """Метод создания объекта модели в БД."""
        db_obj = self.model(**obj.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Base, obj: BaseModel) -> Base:
        """Метод обновления объекта модели в БД."""
        update_data = obj.model_dump()
        for field in db_obj.__mapper__.attrs.keys():
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Base) -> None:
        """Метод удаления объекта модели из БД."""
        await self.db.delete(db_obj)
        await self.db.commit()
