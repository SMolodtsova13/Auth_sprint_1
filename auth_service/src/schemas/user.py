from uuid import UUID

from pydantic import BaseModel, constr

class UserCreate(BaseModel):

    login: constr(min_length=3, max_length=255)
    password: constr(min_length=6)
    first_name: str
    last_name: str


class UserInDB(BaseModel):

    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
