from pydantic import BaseModel


class AuthTokensData(BaseModel):
    id_user: str
    type: str
    access_token: str
    refresh_token: str
