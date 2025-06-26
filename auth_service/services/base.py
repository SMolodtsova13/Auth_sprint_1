from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base
from services.db import DbService


class BaseService:
    """Базовый сервис."""

    def __init__(self, db: AsyncSession, model: Base) -> None:
        self.db = DbService(db, model)

    async def get_obj_or_404(self, id: UUID) -> Base:
        """Метод получения объекта модели по id."""
        obj = await self.db.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Объект не найден.'
            )
        return obj
