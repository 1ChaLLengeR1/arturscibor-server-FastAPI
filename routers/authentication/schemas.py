from pydantic import BaseModel


class LoginUserSchema(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True

class OptionsTokens(BaseModel):
    id_user: str
    refresh_token: str

    class Config:
        orm_mode = True
