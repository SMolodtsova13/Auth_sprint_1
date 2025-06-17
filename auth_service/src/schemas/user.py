from uuid import UUID

from pydantic import BaseModel, constr

from core.constants import (
    LOGIN_MAX_LENGHT, LOGIN_MIN_LENGTH, PASSWORD_MIN_LENGTH
)


class UserCreate(BaseModel):

    login: constr(
        min_length=LOGIN_MIN_LENGTH,
        max_length=LOGIN_MAX_LENGHT
    )
    password: constr(min_length=PASSWORD_MIN_LENGTH)
    first_name: str
    last_name: str


class UserInDB(BaseModel):

    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
