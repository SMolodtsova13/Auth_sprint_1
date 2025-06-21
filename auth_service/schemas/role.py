from uuid import UUID
from pydantic import BaseModel


class RoleCreate(BaseModel):

    name: str


class RoleOperation(BaseModel):
    user_id: UUID
    role_id: UUID

    class Config:
        from_attributes = True
