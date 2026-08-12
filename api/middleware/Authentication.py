from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.common.jwt import decode_access_token
from core.repository.psql.users.one import one_by_id_psql


class JWTAuthenticationMiddleware(HTTPBearer):
    """Dependency (used via Depends()), not ASGI middleware. Decodes the
    bearer token, then re-verifies user_id and role directly against the
    database via one_by_id_psql — not just the token's claims — so a role
    change or a deleted user takes effect immediately instead of waiting
    for the token to expire."""

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

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user, _, ok = one_by_id_psql(user_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if self.roles is not None and user.type not in self.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return {"id_user": user.id, "type": user.type}
