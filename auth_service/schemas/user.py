from uuid import UUID

from pydantic import BaseModel, constr

from core.constants import (
    LOGIN_MAX_LENGHT, LOGIN_MIN_LENGTH, PASSWORD_MIN_LENGTH
)


class SuperUserCreate(BaseModel):

    login: str
    password: str
    first_name: str
    last_name: str


class UserCreate(SuperUserCreate):

    login: constr(min_length=LOGIN_MIN_LENGTH, max_length=LOGIN_MAX_LENGHT)
    password: constr(min_length=PASSWORD_MIN_LENGTH)


class UserInDB(BaseModel):

    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
