import uuid

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.projects.update import router as admin_projects_update_router
from api.endpoints.projects.collection import router as projects_collection_router
from api.endpoints.urls import ADMIN_PROJECTS_UPDATE, PROJECTS_COLLECTION
from core.common.jwt import create_access_token
from tests.api.endpoints.projects.helper import admin_auth_headers, make_client
from tests.core.repository.psql.projects.helper import create_test_project
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminUpdateProject:
    def test_update01_returns_200(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session, name="Portfolio API")

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"numeric": 5},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 200
        assert response.json()["data"]["numeric"] == 5
        assert response.json()["data"]["name"] == "Portfolio API"

    def test_update02_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_projects_update_router)

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=uuid.uuid4()),
            json={"name": "X"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 404

    def test_update03_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session)

        response = client.put(ADMIN_PROJECTS_UPDATE.format(project_id=project.id), json={"name": "X"})

        assert response.status_code == 401

    def test_update04_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"name": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_update05_language_code_edits_only_that_language(self, db_session):
        client = make_client(db_session, admin_projects_update_router, projects_collection_router)
        headers = admin_auth_headers(db_session)
        project = create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"})

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"language_code": "en", "short_description": "Python Snake"},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json()["data"]["short_description"] == "Python Snake"

        pl_collection = client.get(PROJECTS_COLLECTION, params={"lang": "pl"})
        assert pl_collection.json()["data"][0]["short_description"] == "Wąż"

    def test_update06_empty_name_returns_422(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session)

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"name": ""},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 422

    def test_update07_null_name_returns_400(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session)

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"name": None},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidValue"

    def test_update08_technologies_full_replace(self, db_session):
        client = make_client(db_session, admin_projects_update_router)
        project = create_test_project(db_session, technologies=["Python"])

        response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project.id),
            json={"technologies": ["Rust", "Postgres"]},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 200
        assert response.json()["data"]["technologies"] == ["Rust", "Postgres"]
