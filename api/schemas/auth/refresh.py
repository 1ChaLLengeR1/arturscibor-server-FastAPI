from pydantic import BaseModel


class RefreshPayload(BaseModel):
    id_user: str
    refresh_token: str
