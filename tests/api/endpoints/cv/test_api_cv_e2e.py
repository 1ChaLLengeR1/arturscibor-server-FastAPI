import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.cv.upload import router as admin_cv_upload_router
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.cv.get import router as cv_get_router
from api.endpoints.urls import ADMIN_CV_UPLOAD, ADMIN_FILE_CONFIRM, ADMIN_FILE_INIT, ADMIN_FILE_UPLOAD, CV
from config.settings import settings
from tests.api.endpoints.cv.helper import admin_auth_headers, make_client
from tests.core.repository.psql.cv.helper import create_test_cv

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


class TestCvE2E:
    def test_e2e01_seed_public_view_upload_replace(self, db_session, static_root):
        client = make_client(
            db_session,
            cv_get_router,
            admin_cv_upload_router,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
        )
        headers = admin_auth_headers(db_session)

        # 1. Singleton seedowany "migracją" (helper, bo testy nie odpalają alembic).
        create_test_cv(db_session)

        # 2. Publiczny widok przed uploadem - brak przypiętego pliku, 404.
        initial_public = client.get(CV)
        assert initial_public.status_code == 404

        # 3. Pełny cykl file domain: init -> upload -> confirm dla dokumentu PDF.
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
        assert init_response.status_code == 201
        first_file_id = init_response.json()["data"]["file_id"]

        upload_response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=first_file_id),
            content=_PDF_BYTES,
            headers={**headers, "content-type": _PDF_MIME},
        )
        assert upload_response.status_code == 200

        confirm_response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=first_file_id), headers=headers)
        assert confirm_response.status_code == 200

        # 4. Podpięcie CV.
        cv_upload_response = client.put(ADMIN_CV_UPLOAD, json={"file_id": first_file_id}, headers=headers)
        assert cv_upload_response.status_code == 200
        assert cv_upload_response.json()["data"]["file_id"] == first_file_id
        first_saved = next((static_root / "cv").iterdir())
        assert first_saved.is_file()

        # 5. Publiczny widok po uploadzie - serwuje bajty pliku.
        public_after_upload = client.get(CV)
        assert public_after_upload.status_code == 200
        assert public_after_upload.content == _PDF_BYTES
        assert 'filename="cv.pdf"' in public_after_upload.headers["content-disposition"]

        # 6. Podmiana CV - drugi dokument, stary plik kasowany z dysku.
        init_response_2 = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "cv-v2.pdf",
                "size": len(_PDF_BYTES),
                "directory": "cv",
                "file_type": "document",
                "mime_type": _PDF_MIME,
            },
            headers=headers,
        )
        second_file_id = init_response_2.json()["data"]["file_id"]
        client.put(
            ADMIN_FILE_UPLOAD.format(file_id=second_file_id),
            content=_PDF_BYTES,
            headers={**headers, "content-type": _PDF_MIME},
        )
        client.patch(ADMIN_FILE_CONFIRM.format(file_id=second_file_id), headers=headers)

        replace_response = client.put(ADMIN_CV_UPLOAD, json={"file_id": second_file_id}, headers=headers)
        assert replace_response.status_code == 200
        assert replace_response.json()["data"]["file_id"] == second_file_id
        assert not first_saved.exists()

        final_public = client.get(CV)
        assert final_public.status_code == 200
        assert 'filename="cv-v2.pdf"' in final_public.headers["content-disposition"]
