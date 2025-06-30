from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.base import Base
from models.mixins import UUIDMixin, CreatedAtMixin
from core.constants import ROLE_NAME_MAX_LENGTH


class Role(UUIDMixin, CreatedAtMixin, Base):
    """Модель роли."""

    __tablename__ = 'roles'

    name = Column(String(ROLE_NAME_MAX_LENGTH), unique=True, nullable=False)
    user_roles = relationship(
        'UserRole',
        back_populates='role',
        lazy='selectin'
    )


class UserRole(UUIDMixin, Base):
    """Модель роли пользователя."""

    __tablename__ = 'user_roles'

    user_id = Column(
        UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user = relationship(
        'User',
        back_populates='roles',
        lazy='selectin'
    )
    role_id = Column(UUID, ForeignKey('roles.id'))
    role = relationship(
        'Role',
        back_populates='user_roles',
        lazy='selectin'
    )
