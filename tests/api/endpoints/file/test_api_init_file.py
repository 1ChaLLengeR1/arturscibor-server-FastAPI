import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.urls import ADMIN_FILE_INIT
from core.common.jwt import create_access_token
from tests.api.endpoints.file.helper import admin_auth_headers, make_client
from tests.core.repository.psql.users.helper import create_test_user


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    # JWTAuthenticationMiddleware looks the caller up via a standalone session —
    # see tests/api/middleware/test_authentication.py.
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


class TestApiAdminInitFile:
    def test_init01_returns_201(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "photo.png",
                "size": 1024,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": "image/png",
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        assert response.json()["status"] == "SUCCESS"

    def test_init02_response_contains_urls(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "banner.jpg",
                "size": 2048,
                "directory": "tools",
                "file_type": "photo",
                "mime_type": "image/jpeg",
            },
            headers=admin_auth_headers(db_session),
        )

        data = response.json()["data"]
        assert "file_id" in data
        assert data["upload_url"].endswith("/upload")
        assert data["public_url"].startswith("/static/tools/")

    def test_init03_invalid_directory_returns_400(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={"original_name": "photo.png", "size": 512, "directory": "unknown", "file_type": "photo"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidDirectory"

    def test_init04_wrong_extension_for_file_type_returns_400(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={"original_name": "movie.mp4", "size": 512, "directory": "projects", "file_type": "photo"},
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidExtension"

    def test_init05_mime_from_other_family_returns_400(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "photo.png",
                "size": 512,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": "text/html",
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidMimeType"

    def test_init06_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={"original_name": "photo.png", "size": 512, "directory": "projects", "file_type": "photo"},
        )

        assert response.status_code == 401

    def test_init07_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_file_init_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_FILE_INIT,
            json={"original_name": "photo.png", "size": 512, "directory": "projects", "file_type": "photo"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestApiAdminInitFileSanitization:
    def test_sanitize01_path_segments_are_stripped_from_public_url(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "../../../etc/passwd.png",
                "size": 512,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": "image/png",
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        public_url = response.json()["data"]["public_url"]
        assert public_url.startswith("/static/projects/")
        assert ".." not in public_url
        assert public_url.endswith("_passwd.png")

    def test_sanitize02_unsafe_characters_are_replaced(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "moje zdjęcie (1).png",
                "size": 512,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": "image/png",
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 201
        assert response.json()["data"]["public_url"].endswith("_moje_zdj_cie_1.png")

    def test_sanitize03_too_long_name_is_rejected_by_schema(self, db_session):
        client = make_client(db_session, admin_file_init_router)

        response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "a" * 300 + ".png",
                "size": 512,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": "image/png",
            },
            headers=admin_auth_headers(db_session),
        )

        assert response.status_code == 422
