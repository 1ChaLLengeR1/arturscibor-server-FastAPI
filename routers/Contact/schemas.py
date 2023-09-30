from pydantic import BaseModel


class DeleteMessage(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True


class GetIdMessage(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True
