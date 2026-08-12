from dataclasses import dataclass


@dataclass
class AuthTokensResult:
    id_user: str
    type: str
    access_token: str
    refresh_token: str
