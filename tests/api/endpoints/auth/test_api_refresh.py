from api.endpoints.auth.login import router as login_router
from api.endpoints.auth.refresh import router as refresh_router
from tests.api.endpoints.auth.helper import make_client
from tests.core.repository.psql.users.helper import create_test_user


class TestApiRefresh:
    def test_refresh01_invalid_token_returns_401(self, db_session):
        user = create_test_user(db_session, login="eve")
        db_session.commit()
        client = make_client(db_session, refresh_router)

        response = client.post(
            "/api/v1/auth/refresh",
            json={"id_user": str(user.id), "refresh_token": "not-a-real-token"},
        )

        assert response.status_code == 401

    def test_refresh02_e2e_login_then_refresh_with_same_token_succeeds(self, db_session):
        create_test_user(db_session, login="frank", password="secret123")
        db_session.commit()
        client = make_client(db_session, login_router, refresh_router)

        login_response = client.post("/api/v1/auth/login", json={"login": "frank", "password": "secret123"})
        login_data = login_response.json()["data"]

        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"id_user": login_data["id_user"], "refresh_token": login_data["refresh_token"]},
        )

        assert login_response.status_code == 200
        assert refresh_response.status_code == 200
        assert refresh_response.json()["data"]["access_token"]
