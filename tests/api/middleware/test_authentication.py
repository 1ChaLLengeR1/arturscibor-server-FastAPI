import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.middleware.Authentication import JWTAuthenticationMiddleware
from core.common.jwt import create_access_token
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    # JWTAuthenticationMiddleware calls one_by_id_psql() without a request
    # session, so it opens its own via the module-level SessionLocal — which
    # is bound to the regular (non-test) database. Point it at test_engine
    # for the duration of these tests so it sees the users we create below.
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


def make_client() -> TestClient:
    app = FastAPI()

    @app.get("/protected")
    def protected(user: dict = Depends(JWTAuthenticationMiddleware())):
        return user

    @app.get("/admin-only")
    def admin_only(user: dict = Depends(JWTAuthenticationMiddleware(roles=["admin"]))):
        return user

    return TestClient(app)


class TestJWTAuthenticationMiddleware:
    def test_authentication01_valid_token_returns_user(self, db_session):
        user = create_test_user(db_session, login="carol", type="guest")
        db_session.commit()
        token = create_access_token(str(user.id))

        response = make_client().get("/protected", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["id_user"] == str(user.id)

    def test_authentication02_missing_token_returns_401(self):
        response = make_client().get("/protected")

        assert response.status_code == 401

    def test_authentication03_wrong_role_returns_403(self, db_session):
        user = create_test_user(db_session, login="dave", type="guest")
        db_session.commit()
        token = create_access_token(str(user.id))

        response = make_client().get("/admin-only", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403
