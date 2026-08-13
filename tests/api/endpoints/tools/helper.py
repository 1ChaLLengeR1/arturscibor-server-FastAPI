from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.exception_handlers import register_exception_handlers
from core.common.jwt import create_access_token
from database.psql.database import get_db
from tests.core.repository.psql.users.helper import create_test_user


def make_client(db_session: Session, *routers: APIRouter) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    for router in routers:
        app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


def admin_auth_headers(db_session: Session) -> dict:
    """Tworzy admina i zwraca nagłówek Bearer.

    JWTAuthenticationMiddleware weryfikuje usera przez standalone sesję
    (poza `db_session` requestu), więc user musi być realnie zacommitowany —
    sam flush() nie wystarczy (patrz tests/api/middleware/test_authentication.py).
    """
    admin = create_test_user(db_session, type="admin")
    db_session.commit()
    token = create_access_token(str(admin.id))
    return {"Authorization": f"Bearer {token}"}
