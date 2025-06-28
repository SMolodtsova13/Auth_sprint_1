from pydantic import BaseModel


class UserData(BaseModel):
    """Модель данных пользователя для тестов."""

    login: str
    password: str
    first_name: str
    last_name: str
