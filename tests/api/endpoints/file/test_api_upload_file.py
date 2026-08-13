import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.urls import ADMIN_FILE_UPLOAD
from config.settings import settings
from core.common.jwt import create_access_token
from tests.api.endpoints.file.helper import admin_auth_headers, make_client
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
    """Uploady lecą do tmp — test nie zaśmieca realnego static/files/."""
    monkeypatch.setattr(settings, "static_root", tmp_path)
    return tmp_path


def _init_file(client, headers, *, directory: str = "projects") -> str:
    response = client.post(
        "/api/v1/admin/file/init",
        json={
            "original_name": "naruto.png",
            "size": _IMAGE_SIZE,
            "directory": directory,
            "file_type": "photo",
            "mime_type": _IMAGE_MIME,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["data"]["file_id"]


class TestApiAdminUploadFile:
    def test_upload01_returns_200_and_status_completed(self, db_session):
        client = make_client(db_session, admin_file_init_router, admin_file_upload_router)
        headers = admin_auth_headers(db_session)
        file_id = _init_file(client, headers)

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )

        assert response.status_code == 200
        assert response.json()["data"]["status"] == "completed"

    def test_upload02_bytes_land_on_disk(self, db_session, static_root):
        client = make_client(db_session, admin_file_init_router, admin_file_upload_router)
        headers = admin_auth_headers(db_session)
        file_id = _init_file(client, headers, directory="tools")

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )

        public_url = response.json()["data"]["url"]
        saved = static_root / public_url.removeprefix("/static/")
        assert saved.is_file()
        assert saved.read_bytes() == _IMAGE_BYTES

    def test_upload03_nonexistent_file_returns_404(self, db_session):
        client = make_client(db_session, admin_file_upload_router)

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=uuid.uuid4()),
            content=_IMAGE_BYTES,
            headers={**admin_auth_headers(db_session), "content-type": _IMAGE_MIME},
        )

        assert response.status_code == 404

    def test_upload04_mime_mismatch_returns_400(self, db_session):
        client = make_client(db_session, admin_file_init_router, admin_file_upload_router)
        headers = admin_auth_headers(db_session)
        file_id = _init_file(client, headers)

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": "image/gif"},
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "MimeTypeMismatch"

    def test_upload05_octet_stream_is_accepted(self, db_session):
        client = make_client(db_session, admin_file_init_router, admin_file_upload_router)
        headers = admin_auth_headers(db_session)
        file_id = _init_file(client, headers)

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": "application/octet-stream"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["status"] == "completed"

    def test_upload06_repeated_upload_on_completed_file_returns_400(self, db_session):
        client = make_client(db_session, admin_file_init_router, admin_file_upload_router)
        headers = admin_auth_headers(db_session)
        file_id = _init_file(client, headers)
        client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidStatus"

    def test_upload07_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_file_upload_router)

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=uuid.uuid4()),
            content=_IMAGE_BYTES,
            headers={"content-type": _IMAGE_MIME},
        )

        assert response.status_code == 401

    def test_upload08_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_file_upload_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=uuid.uuid4()),
            content=_IMAGE_BYTES,
            headers={"Authorization": f"Bearer {token}", "content-type": _IMAGE_MIME},
        )

        assert response.status_code == 403
