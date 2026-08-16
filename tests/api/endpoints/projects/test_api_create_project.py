import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.projects.create import router as admin_projects_create_router
from api.endpoints.urls import ADMIN_PROJECTS_CREATE
from core.common.jwt import create_access_token
from database.psql.models.projects import Projects
from tests.api.endpoints.projects.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminCreateProject:
    def test_create01_returns_201(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={
                "name": "Portfolio API",
                "short_description": {"pl": "Krótki opis", "en": "Short description"},
                "level": "advanced",
                "technologies": ["Python", "FastAPI"],
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Portfolio API"
        assert response.json()["data"]["level"] == "advanced"

    def test_create02_starts_with_no_images(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={"name": "Portfolio API"},
            headers=admin_auth_headers(db_session),
        )

        assert response.json()["data"]["images"] == []

    def test_create03_missing_name_returns_422(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(ADMIN_PROJECTS_CREATE, json={}, headers=admin_auth_headers(db_session))

        assert response.status_code == 422

    def test_create04_invalid_level_returns_422(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={"name": "Portfolio API", "level": "guru"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 422

    def test_create05_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(ADMIN_PROJECTS_CREATE, json={"name": "Portfolio API"})

        assert response.status_code == 401

    def test_create06_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_projects_create_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={"name": "Portfolio API"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_create07_short_description_missing_en_key_returns_422(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={"name": "Portfolio API", "short_description": {"pl": "Krótki opis"}},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 422

    def test_create08_extra_language_is_accepted_and_stored(self, db_session):
        client = make_client(db_session, admin_projects_create_router)

        response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={
                "name": "Portfolio API",
                "short_description": {"pl": "Krótki opis", "en": "Short description", "de": "Kurzbeschreibung"},
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        project_id = response.json()["data"]["id"]
        stored = db_session.query(Projects).filter(Projects.id == project_id).one()
        assert stored.short_description == {"pl": "Krótki opis", "en": "Short description", "de": "Kurzbeschreibung"}
