import uuid

from sqlalchemy.orm import Session

from core.common.bcrypt_password import hash_password
from database.psql.models.users import Users


def create_test_user(
    db: Session,
    *,
    login: str | None = None,
    password: str = "password123",
    type: str = "guest",
) -> Users:
    user = Users(
        login=login or f"user-{uuid.uuid4().hex[:8]}",
        password=hash_password(password),
        type=type,
    )
    db.add(user)
    db.flush()
    return user
