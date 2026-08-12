from pydantic import BaseModel, Field


class LoginPayload(BaseModel):
    login: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=32)
