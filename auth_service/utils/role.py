from functools import wraps
from fastapi import HTTPException
from http import HTTPStatus


def permission_required(permission_name: str):
    """
    Декоратор для проверки наличия у пользователя указанного разрешения.
    Ожидается, что в обернутый метод передается параметр current_user_id.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            current_user_id = kwargs.get("current_user_id")
            if not current_user_id:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            if not await self.has_permission(current_user_id, permission_name):
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail=f"У вас нет прав '{permission_name}' для выполнения этого действия"
                )
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator
