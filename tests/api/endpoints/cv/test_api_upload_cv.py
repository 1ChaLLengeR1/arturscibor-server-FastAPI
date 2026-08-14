import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.cv.upload import router as admin_cv_upload_router
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.urls import ADMIN_CV_UPLOAD, ADMIN_FILE_CONFIRM, ADMIN_FILE_INIT, ADMIN_FILE_UPLOAD
from config.settings import settings
from core.common.jwt import create_access_token
from database.psql.models.file import FileType
from tests.api.endpoints.cv.helper import admin_auth_headers, make_client
from tests.core.repository.psql.cv.helper import create_test_cv
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.users.helper import create_test_user

_PDF_BYTES = b"%PDF-1.4 fake pdf content for tests"
_PDF_MIME = "application/pdf"


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


def _confirmed_document_file_id(client, headers) -> str:
    init_response = client.post(
        ADMIN_FILE_INIT,
        json={
            "original_name": "cv.pdf",
            "size": len(_PDF_BYTES),
            "directory": "cv",
            "file_type": "document",
            "mime_type": _PDF_MIME,
        },
        headers=headers,
    )
    file_id = init_response.json()["data"]["file_id"]
    client.put(
        ADMIN_FILE_UPLOAD.format(file_id=file_id),
        content=_PDF_BYTES,
        headers={**headers, "content-type": _PDF_MIME},
    )
    client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)
    return file_id


class TestApiAdminUploadCv:
    def test_upload01_returns_200_with_url(self, db_session):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_cv_upload_router,
        )
        headers = admin_auth_headers(db_session)
        create_test_cv(db_session)
        file_id = _confirmed_document_file_id(client, headers)

        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": file_id}, headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["file_id"] == file_id
        assert response.json()["data"]["url"].startswith("/static/cv/")

    def test_upload02_pending_file_returns_400(self, db_session):
        client = make_client(db_session, admin_cv_upload_router)
        headers = admin_auth_headers(db_session)
        create_test_cv(db_session)
        file = create_test_file(db_session, original_name="cv.pdf", file_type=FileType.DOCUMENT)

        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": str(file.id)}, headers=headers)

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidStatus"

    def test_upload03_non_document_file_returns_400(self, db_session):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_cv_upload_router,
        )
        headers = admin_auth_headers(db_session)
        create_test_cv(db_session)
        image_bytes = b"\x89PNG fake"
        init_response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "not-a-cv.png",
                "size": len(image_bytes),
                "directory": "cv",
                "file_type": "photo",
                "mime_type": "image/png",
            },
            headers=headers,
        )
        file_id = init_response.json()["data"]["file_id"]
        client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=image_bytes,
            headers={**headers, "content-type": "image/png"},
        )
        client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)

        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": file_id}, headers=headers)

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidFileType"

    def test_upload04_not_seeded_returns_404(self, db_session):
        client = make_client(db_session, admin_cv_upload_router)
        headers = admin_auth_headers(db_session)
        file = create_test_file(db_session, original_name="cv.pdf")

        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": str(file.id)}, headers=headers)

        assert response.status_code == 404

    def test_upload05_replacing_cv_deletes_old_file(self, db_session, static_root):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_cv_upload_router,
        )
        headers = admin_auth_headers(db_session)
        create_test_cv(db_session)
        first_file_id = _confirmed_document_file_id(client, headers)
        client.put(ADMIN_CV_UPLOAD, json={"file_id": first_file_id}, headers=headers)
        first_saved = next((static_root / "cv").iterdir())
        assert first_saved.is_file()

        second_file_id = _confirmed_document_file_id(client, headers)
        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": second_file_id}, headers=headers)

        assert response.status_code == 200
        assert response.json()["data"]["file_id"] == second_file_id
        assert not first_saved.exists()

    def test_upload06_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_cv_upload_router)
        create_test_cv(db_session)
        file = create_test_file(db_session, original_name="cv.pdf")

        response = client.put(ADMIN_CV_UPLOAD, json={"file_id": str(file.id)})

        assert response.status_code == 401

    def test_upload07_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_cv_upload_router)
        create_test_cv(db_session)
        file = create_test_file(db_session, original_name="cv.pdf")
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.put(
            ADMIN_CV_UPLOAD,
            json={"file_id": str(file.id)},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
