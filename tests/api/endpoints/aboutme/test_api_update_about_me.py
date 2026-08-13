import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.aboutme.update import router as admin_aboutme_update_router
from api.endpoints.urls import ADMIN_ABOUT_ME_UPDATE
from core.common.jwt import create_access_token
from tests.api.endpoints.aboutme.helper import admin_auth_headers, make_client
from tests.core.repository.psql.aboutme.helper import create_test_about_me
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminUpdateAboutMe:
    def test_update01_returns_200(self, db_session):
        client = make_client(db_session, admin_aboutme_update_router)
        create_test_about_me(db_session, name="Old Name")

        response = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"name": "New Name"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 200
        assert response.json()["data"]["name"] == "New Name"

    def test_update02_not_seeded_returns_404(self, db_session):
        client = make_client(db_session, admin_aboutme_update_router)

        response = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"name": "X"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 404

    def test_update03_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_aboutme_update_router)
        create_test_about_me(db_session)

        response = client.put(ADMIN_ABOUT_ME_UPDATE, json={"name": "X"})

        assert response.status_code == 401

    def test_update04_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_aboutme_update_router)
        create_test_about_me(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"name": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_update05_language_code_edits_only_that_language(self, db_session):
        client = make_client(db_session, admin_aboutme_update_router)
        headers = admin_auth_headers(db_session)
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})

        response = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"language_code": "en", "job_title": "Backend Developer"},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["job_title"] == "Backend Developer"

        pl_response = client.put(
            ADMIN_ABOUT_ME_UPDATE, json={"language_code": "pl", "name": "Unchanged"}, headers=headers
        )
        # nazwa nietłumaczalna zmienia się niezależnie od language_code, ale
        # job_title dla pl powinno zostać nietknięte przez poprzedni update na "en"
        assert pl_response.json()["data"]["job_title"] == "Programista"
