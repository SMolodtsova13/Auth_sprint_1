from datetime import datetime, timedelta

from jose import jwt
from core.config import settings


def create_access_token(sub: str) -> str:
    """
    Генерирует JWT access token с коротким сроком действия.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {'sub': sub, 'type': 'access', 'exp': expire}
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(sub: str, jti: str) -> str:
    """Генерирует JWT refresh token с долгим сроком действия."""
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {'sub': sub, 'type': 'refresh', 'jti': jti, 'exp': expire}
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
