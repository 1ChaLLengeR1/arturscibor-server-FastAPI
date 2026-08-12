from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.common.jwt import decode_access_token


class JWTAuthenticationMiddleware(HTTPBearer):
    """Dependency (used via Depends()), not ASGI middleware. Decodes the
    bearer token and optionally enforces the caller's role (embedded in the
    token as the `role` claim at login — see core/handler/auth/login.py)."""

    def __init__(self, roles: list[str] | None = None, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)
        self.roles = roles

    async def __call__(self, request: Request) -> dict[str, Any]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        try:
            payload = decode_access_token(credentials.credentials)
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

        if self.roles is not None and payload.get("role") not in self.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return payload
