from functools import wraps
from fastapi import HTTPException
from http import HTTPStatus


def permission_required(permission_name: str):
    """
    Декоратор для проверки наличия у пользователя указанного разрешения.
    Ожидается, что в обернутый метод передается параметр current_user.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail='Требуется аутентификация'
                )
            for obj in current_user.roles:
                if obj.role.name == permission_name:
                    return await func(self, *args, **kwargs)
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=f"У вас нет прав '{permission_name}' для выполнения этого действия"
            )
        return wrapper
    return decorator
