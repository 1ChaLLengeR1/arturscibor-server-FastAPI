from pydantic import BaseModel


class ItemDeleteTools(BaseModel):
    id: str | None = None

    class Config:
        orm_mode = True
