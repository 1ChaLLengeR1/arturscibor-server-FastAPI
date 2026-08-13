import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.collection import router as admin_file_collection_router
from api.endpoints.urls import ADMIN_FILE_COLLECTION
from core.common.jwt import create_access_token
from database.psql.models.file import FileType
from tests.api.endpoints.file.helper import admin_auth_headers, make_client
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminCollectionFiles:
    def test_collection01_returns_200_with_empty_list(self, db_session):
        client = make_client(db_session, admin_file_collection_router)

        response = client.get(ADMIN_FILE_COLLECTION, headers=admin_auth_headers(db_session))

        assert response.status_code == 200
        body = response.json()["data"]
        assert body["items"] == []
        assert body["pagination"]["total"] == 0

    def test_collection02_returns_created_files(self, db_session):
        client = make_client(db_session, admin_file_collection_router)
        headers = admin_auth_headers(db_session)
        create_test_file(db_session, directory="projects")
        create_test_file(db_session, directory="tools")

        response = client.get(ADMIN_FILE_COLLECTION, headers=headers)

        assert response.json()["data"]["pagination"]["total"] == 2

    def test_collection03_filters_by_directory(self, db_session):
        client = make_client(db_session, admin_file_collection_router)
        headers = admin_auth_headers(db_session)
        create_test_file(db_session, directory="projects")
        create_test_file(db_session, directory="tools")

        response = client.get(ADMIN_FILE_COLLECTION, params={"directory": "projects"}, headers=headers)

        data = response.json()["data"]
        assert data["pagination"]["total"] == 1
        assert data["items"][0]["directory"] == "projects"

    def test_collection04_filters_by_file_type(self, db_session):
        client = make_client(db_session, admin_file_collection_router)
        headers = admin_auth_headers(db_session)
        create_test_file(db_session, file_type=FileType.PHOTO, name="a.png")
        create_test_file(db_session, file_type=FileType.VIDEO, name="b.mp4", mime_type="video/mp4")

        response = client.get(ADMIN_FILE_COLLECTION, params={"file_type": "video"}, headers=headers)

        data = response.json()["data"]
        assert data["pagination"]["total"] == 1
        assert data["items"][0]["file_type"] == "video"

    def test_collection05_pagination(self, db_session):
        client = make_client(db_session, admin_file_collection_router)
        headers = admin_auth_headers(db_session)
        for i in range(3):
            create_test_file(db_session, name=f"file-{i}.png")

        response = client.get(ADMIN_FILE_COLLECTION, params={"limit": 2, "offset": 0}, headers=headers)

        data = response.json()["data"]
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["has_more"] is True
        assert len(data["items"]) == 2

    def test_collection06_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_file_collection_router)

        response = client.get(ADMIN_FILE_COLLECTION)

        assert response.status_code == 401

    def test_collection07_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_file_collection_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.get(ADMIN_FILE_COLLECTION, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403
