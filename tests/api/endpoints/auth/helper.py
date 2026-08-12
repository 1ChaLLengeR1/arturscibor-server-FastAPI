from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.exception_handlers import register_exception_handlers
from database.psql.database import get_db


def make_client(db_session: Session, *routers: APIRouter) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    for router in routers:
        app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)
