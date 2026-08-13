import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.work.create import router as admin_work_create_router
from api.endpoints.urls import ADMIN_WORK_CREATE
from core.common.jwt import create_access_token
from tests.api.endpoints.work.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminCreateWork:
    def test_create01_returns_201(self, db_session):
        client = make_client(db_session, admin_work_create_router)

        response = client.post(
            ADMIN_WORK_CREATE,
            json={"company_name": "SPINETIME", "numeric": 1},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        assert response.json()["data"]["company_name"] == "SPINETIME"

    def test_create02_starts_with_no_items(self, db_session):
        client = make_client(db_session, admin_work_create_router)

        response = client.post(
            ADMIN_WORK_CREATE, json={"company_name": "SPINETIME"}, headers=admin_auth_headers(db_session)
        )

        assert response.json()["data"]["items"] == []

    def test_create03_missing_company_name_returns_422(self, db_session):
        client = make_client(db_session, admin_work_create_router)

        response = client.post(ADMIN_WORK_CREATE, json={}, headers=admin_auth_headers(db_session))

        assert response.status_code == 422

    def test_create04_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_work_create_router)

        response = client.post(ADMIN_WORK_CREATE, json={"company_name": "SPINETIME"})

        assert response.status_code == 401

    def test_create05_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_work_create_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_WORK_CREATE,
            json={"company_name": "SPINETIME"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
