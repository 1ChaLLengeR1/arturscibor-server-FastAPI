from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.aboutme.get import router as aboutme_get_router
from api.endpoints.admin.aboutme.images.attach import router as admin_aboutme_image_attach_router
from api.endpoints.admin.aboutme.images.detach import router as admin_aboutme_image_detach_router
from api.endpoints.admin.aboutme.update import router as admin_aboutme_update_router
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.urls import (
    ABOUT_ME,
    ADMIN_ABOUT_ME_IMAGE_ATTACH,
    ADMIN_ABOUT_ME_IMAGE_DETACH,
    ADMIN_ABOUT_ME_UPDATE,
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
)
from config.settings import settings
from tests.api.endpoints.aboutme.helper import admin_auth_headers, make_client
from tests.core.repository.psql.aboutme.helper import create_test_about_me

_TEST_IMAGE = Path(__file__).resolve().parents[3] / "files_for_tests" / "Patryk, fortnite,naruto.png"
_IMAGE_BYTES = _TEST_IMAGE.read_bytes()
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


class TestAboutMeE2E:
    def test_e2e01_seed_update_both_languages_attach_image_public_view_detach(self, db_session, static_root):
        client = make_client(
            db_session,
            aboutme_get_router,
            admin_aboutme_update_router,
            admin_aboutme_image_attach_router,
            admin_aboutme_image_detach_router,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
        )
        headers = admin_auth_headers(db_session)

        # 1. Singleton seedowany "migracją" (tu: helperem, migracje w testach nie
        #    lecą — patrz tests/core/repository/psql/aboutme/helper.py).
        create_test_about_me(db_session, name="Artur Ścibor")

        # 2. Admin wypełnia treść PL.
        update_pl = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"language_code": "pl", "job_title": "Programista Backendowy", "body_markdown": "# O mnie\nCześć!"},
            headers=headers,
        )
        assert update_pl.status_code == 200
        assert update_pl.json()["data"]["job_title"] == "Programista Backendowy"

        # 3. Admin wypełnia treść EN.
        update_en = client.put(
            ADMIN_ABOUT_ME_UPDATE,
            json={"language_code": "en", "job_title": "Backend Developer", "body_markdown": "# About me\nHi!"},
            headers=headers,
        )
        assert update_en.status_code == 200
        assert update_en.json()["data"]["job_title"] == "Backend Developer"

        # 4. Pełny cykl file domain: init -> upload -> confirm.
        init_response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "naruto.png",
                "size": len(_IMAGE_BYTES),
                "directory": "aboutme",
                "file_type": "photo",
                "mime_type": _IMAGE_MIME,
            },
            headers=headers,
        )
        assert init_response.status_code == 201
        file_id = init_response.json()["data"]["file_id"]

        upload_response = client.put(
            ADMIN_FILE_UPLOAD.format(file_id=file_id),
            content=_IMAGE_BYTES,
            headers={**headers, "content-type": _IMAGE_MIME},
        )
        assert upload_response.status_code == 200

        confirm_response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)
        assert confirm_response.status_code == 200

        # 5. Podpięcie zdjęcia.
        attach_response = client.post(ADMIN_ABOUT_ME_IMAGE_ATTACH, json={"file_id": file_id}, headers=headers)
        assert attach_response.status_code == 200
        assert len(attach_response.json()["data"]["images"]) == 1

        # 6. Publiczny widok, bez auth, w obu językach.
        public_pl = client.get(ABOUT_ME)
        assert public_pl.status_code == 200
        assert public_pl.json()["data"]["job_title"] == "Programista Backendowy"
        assert len(public_pl.json()["data"]["images"]) == 1

        public_en = client.get(ABOUT_ME, params={"lang": "en"})
        assert public_en.json()["data"]["job_title"] == "Backend Developer"

        # 7. Odpięcie zdjęcia realnie kasuje bajty z dysku.
        saved = next((static_root / "aboutme").iterdir())
        assert saved.is_file()
        detach_response = client.delete(ADMIN_ABOUT_ME_IMAGE_DETACH.format(file_id=file_id), headers=headers)
        assert detach_response.status_code == 200
        assert detach_response.json()["data"]["images"] == []
        assert not saved.exists()

        final_public = client.get(ABOUT_ME)
        assert final_public.json()["data"]["images"] == []
