from api.endpoints.auth.login import router as login_router
from tests.api.endpoints.auth.helper import make_client
from tests.core.repository.psql.users.helper import create_test_user


class TestApiLogin:
    def test_login01_returns_tokens(self, db_session):
        create_test_user(db_session, login="alice", password="secret123")
        db_session.commit()
        client = make_client(db_session, login_router)

        response = client.post("/api/v1/auth/login", json={"login": "alice", "password": "secret123"})

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["access_token"]
        assert data["refresh_token"]

    def test_login02_wrong_password_returns_401(self, db_session):
        create_test_user(db_session, login="alice", password="secret123")
        db_session.commit()
        client = make_client(db_session, login_router)

        response = client.post("/api/v1/auth/login", json={"login": "alice", "password": "wrong-password"})

        assert response.status_code == 401
