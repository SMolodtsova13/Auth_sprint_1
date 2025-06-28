from uuid import UUID

from pydantic import BaseModel


class BaseUUID(BaseModel):
    """Базовая схема с полем ID."""

    id: UUID
