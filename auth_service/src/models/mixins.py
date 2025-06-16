import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    """Миксин UUID."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )


class CreatedAtMixin:
    """Миксин даты создания."""

    created_at = Column(DateTime(timezone=True), default=datetime.now)
