from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from models.base import Base
from models.mixins import UUIDMixin, CreatedAtMixin
from core.constants import (
    LOGIN_MAX_LENGHT, NAME_MAX_LENGHT, PASSWORD_MAX_LENGHT,
    ROLE_NAME_MAX_LENGTH, USER_AGENT_MAX_LENGHT
)


class User(UUIDMixin, CreatedAtMixin, Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    login = Column(String(LOGIN_MAX_LENGHT), unique=True, nullable=False)
    password = Column(String(PASSWORD_MAX_LENGHT), nullable=False)
    first_name = Column(String(NAME_MAX_LENGHT))
    last_name = Column(String(NAME_MAX_LENGHT))
    login_history = relationship('LoginHistory', back_populates='user')
    roles = relationship('UserRole', back_populates='user')

    def __init__(
        self,
        login: str,
        password: str,
        first_name: str,
        last_name: str
    ) -> None:
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class LoginHistory(UUIDMixin, Base):
    """Модель истории входов пользователя."""

    __tablename__ = 'login_history'

    user_id = Column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='login_history')
    user_agent = Column(String(USER_AGENT_MAX_LENGHT))
    login_at = Column(DateTime, nullable=False)


class Role(UUIDMixin, CreatedAtMixin, Base):
    """Модель роли."""

    __tablename__ = 'roles'

    name = Column(String(ROLE_NAME_MAX_LENGTH), unique=True, nullable=False)
    user_roles = relationship('UserRole', back_populates='role')


class UserRole(UUIDMixin, Base):
    """Модель роли пользователя."""

    __tablename__ = 'user_roles'

    user_id = Column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='roles')
    role_id = Column(UUID, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='user_roles')
