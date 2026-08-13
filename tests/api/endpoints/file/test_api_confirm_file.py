import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.urls import ADMIN_FILE_CONFIRM, ADMIN_FILE_UPLOAD
from config.settings import settings
from core.common.jwt import create_access_token
from database.psql.models.file import FileStatus
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
    """Confirm sprawdza obecność bajtów na dysku — kierujemy go na tmp."""
    monkeypatch.setattr(settings, "static_root", tmp_path)
    return tmp_path


def _init_and_upload(client, headers) -> str:
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
    upload_response = client.put(
        ADMIN_FILE_UPLOAD.format(file_id=file_id),
        content=_IMAGE_BYTES,
        headers={**headers, "content-type": _IMAGE_MIME},
    )
    assert upload_response.status_code == 200
    return file_id


class TestApiAdminConfirmFile:
    def test_confirm01_full_flow_returns_200_and_confirmed(self, db_session):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_confirm_router
        )
        headers = admin_auth_headers(db_session)
        file_id = _init_and_upload(client, headers)

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["status"] == "confirmed"

    def test_confirm02_idempotent_on_already_confirmed(self, db_session):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_confirm_router
        )
        headers = admin_auth_headers(db_session)
        file_id = _init_and_upload(client, headers)
        client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["status"] == "confirmed"

    def test_confirm03_pending_file_returns_400(self, db_session):
        client = make_client(db_session, admin_file_confirm_router)
        headers = admin_auth_headers(db_session)
        file = create_test_file(db_session, status=FileStatus.PENDING)
        db_session.commit()

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file.id), headers=headers)

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidStatus"

    def test_confirm04_missing_bytes_on_disk_returns_400(self, db_session):
        client = make_client(db_session, admin_file_confirm_router)
        headers = admin_auth_headers(db_session)
        file = create_test_file(db_session, status=FileStatus.COMPLETED)
        db_session.commit()

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file.id), headers=headers)

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "MissingOnDisk"

    def test_confirm05_nonexistent_file_returns_404(self, db_session):
        client = make_client(db_session, admin_file_confirm_router)

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=uuid.uuid4()), headers=admin_auth_headers(db_session))

        assert response.status_code == 404

    def test_confirm06_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_file_confirm_router)

        response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=uuid.uuid4()))

        assert response.status_code == 401

    def test_confirm07_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_file_confirm_router)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.patch(
            ADMIN_FILE_CONFIRM.format(file_id=uuid.uuid4()), headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
