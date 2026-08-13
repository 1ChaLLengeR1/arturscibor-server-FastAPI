import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.tools.create import router as admin_tools_create_router
from api.endpoints.urls import ADMIN_TOOLS_CREATE
from core.common.jwt import create_access_token
from tests.api.endpoints.tools.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminCreateTool:
    def test_create01_returns_201(self, db_session):
        client = make_client(db_session, admin_tools_create_router)

        response = client.post(
            ADMIN_TOOLS_CREATE,
            json={"name": "Python", "information": "Backend language", "progress": 80, "numeric": 1},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Python"

    def test_create02_starts_with_no_images(self, db_session):
        client = make_client(db_session, admin_tools_create_router)

        response = client.post(
            ADMIN_TOOLS_CREATE, json={"name": "Python"}, headers=admin_auth_headers(db_session)
        )

        assert response.json()["data"]["images"] == []

    def test_create03_missing_name_returns_422(self, db_session):
        client = make_client(db_session, admin_tools_create_router)

        response = client.post(ADMIN_TOOLS_CREATE, json={}, headers=admin_auth_headers(db_session))

        assert response.status_code == 422

    def test_create04_progress_out_of_range_returns_422(self, db_session):
        client = make_client(db_session, admin_tools_create_router)

        response = client.post(
            ADMIN_TOOLS_CREATE, json={"name": "Python", "progress": 150}, headers=admin_auth_headers(db_session)
        )

        assert response.status_code == 422

    def test_create05_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_tools_create_router)

        response = client.post(ADMIN_TOOLS_CREATE, json={"name": "Python"})

        assert response.status_code == 401

    def test_create06_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_tools_create_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_TOOLS_CREATE, json={"name": "Python"}, headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
