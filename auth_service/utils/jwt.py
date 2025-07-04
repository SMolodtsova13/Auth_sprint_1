from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

from core.config import settings

scheme = HTTPBearer()


def encode_jwt(to_encode: dict) -> str:
    """Кодирует JWT."""
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def create_access_token(
    sub: str,
    device_id: str,
) -> str:
    """
    Генерирует JWT access token с коротким сроком действия.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode = {
        'sub': sub,
        'type': 'access',
        'device_id': device_id,
        'exp': expire
    }
    return encode_jwt(to_encode)


def create_refresh_token(sub: str, device_id: str) -> str:
    """Генерирует JWT refresh token с долгим сроком действия."""
    expire = datetime.utcnow() + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode = {
        'sub': sub,
        'type': 'refresh',
        'device_id': device_id,
        'exp': expire
    }
    return encode_jwt(to_encode)


def decode_jwt(
    token: str,
    verify_exp: bool = True,
    token_type: str | None = None
) -> dict:
    """Декодирует JWT и проверяет тип токена (access/refresh)."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={'verify_exp': verify_exp}
        )
        if token_type and payload.get('type') != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверный тип токена'
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен'
        )
