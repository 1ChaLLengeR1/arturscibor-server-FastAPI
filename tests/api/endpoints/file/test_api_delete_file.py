import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.delete import router as admin_file_delete_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.urls import ADMIN_FILE_DELETE, ADMIN_FILE_UPLOAD
from config.settings import settings
from core.common.jwt import create_access_token
from database.psql.models.file import File
from tests.api.endpoints.file.helper import admin_auth_headers, make_client
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.users.helper import create_test_user

_TEST_IMAGE = Path(__file__).resolve().parents[3] / "files_for_tests" / "Patryk, fortnite,naruto.png"
_IMAGE_BYTES = _TEST_IMAGE.read_bytes()
_IMAGE_SIZE = len(_IMAGE_BYTES)
_IMAGE_MIME = "image/png"


@pytest.fixture(autouse=True)
def _standalone_sessions_use_test_db(monkeypatch, test_engine):
    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine),
    )


@pytest.fixture(autouse=True)
def static_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "static_root", tmp_path)
    return tmp_path


class TestApiAdminDeleteFile:
    def test_delete01_returns_200_on_success(self, db_session):
        client = make_client(db_session, admin_file_delete_router)
        headers = admin_auth_headers(db_session)
        file = create_test_file(db_session)

        response = client.delete(ADMIN_FILE_DELETE.format(file_id=file.id), headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["deleted"] is True
        assert response.json()["data"]["id"] == str(file.id)

    def test_delete02_removes_row_from_db(self, db_session):
        client = make_client(db_session, admin_file_delete_router)
        headers = admin_auth_headers(db_session)
        file = create_test_file(db_session)

        client.delete(ADMIN_FILE_DELETE.format(file_id=file.id), headers=headers)

        assert db_session.query(File).filter(File.id == file.id).first() is None

    def test_delete03_removes_bytes_from_disk(self, db_session, static_root):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_delete_router
        )
        headers = admin_auth_headers(db_session)
        init_response = client.post(
            "/api/v1/admin/file/init",
            json={
                "original_name": "naruto.png",
                "size": _IMAGE_SIZE,
                "directory": "projects",
                "file_type": "photo",
                "mime_type": _IMAGE_MIME,
            },
            headers=headers,
        )
        file_id = init_response.json()["data"]["file_id"]
        client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )
        saved = next((static_root / "projects").iterdir())
        assert saved.is_file()

        client.delete(ADMIN_FILE_DELETE.format(file_id=file_id), headers=headers)

        assert not saved.exists()

    def test_delete04_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_file_delete_router)

        response = client.delete(ADMIN_FILE_DELETE.format(file_id=uuid.uuid4()), headers=admin_auth_headers(db_session))

        assert response.status_code == 404

    def test_delete05_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_file_delete_router)
        file = create_test_file(db_session)

        response = client.delete(ADMIN_FILE_DELETE.format(file_id=file.id))

        assert response.status_code == 401

    def test_delete06_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_file_delete_router)
        file = create_test_file(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.delete(
            ADMIN_FILE_DELETE.format(file_id=file.id), headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
