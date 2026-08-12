from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from config.settings import settings


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=settings.access_token_expire_hours)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_admin_token, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=settings.refresh_token_expire_hours)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.refresh_admin_token, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_admin_token, algorithms=[settings.algorithm])


def decode_refresh_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.refresh_admin_token, algorithms=[settings.algorithm])
