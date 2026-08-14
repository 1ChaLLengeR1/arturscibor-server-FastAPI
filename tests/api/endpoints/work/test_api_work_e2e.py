from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.work.create import router as admin_work_create_router
from api.endpoints.admin.work.delete import router as admin_work_delete_router
from api.endpoints.admin.work.items.create import router as admin_work_item_create_router
from api.endpoints.admin.work.items.delete import router as admin_work_item_delete_router
from api.endpoints.admin.work.items.update import router as admin_work_item_update_router
from api.endpoints.admin.work.logo.update import router as admin_work_logo_update_router
from api.endpoints.admin.work.update import router as admin_work_update_router
from api.endpoints.urls import (
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
    ADMIN_WORK_CREATE,
    ADMIN_WORK_DELETE,
    ADMIN_WORK_ITEM_CREATE,
    ADMIN_WORK_ITEM_DELETE,
    ADMIN_WORK_ITEM_UPDATE,
    ADMIN_WORK_LOGO,
    ADMIN_WORK_UPDATE,
    WORK_COLLECTION,
)
from api.endpoints.work.collection import router as work_collection_router
from config.settings import settings
from tests.api.endpoints.work.helper import admin_auth_headers, make_client

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


class TestWorkE2E:
    def test_e2e01_full_lifecycle(self, db_session, static_root):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_work_create_router,
            admin_work_update_router,
            admin_work_delete_router,
            admin_work_logo_update_router,
            admin_work_item_create_router,
            admin_work_item_update_router,
            admin_work_item_delete_router,
            work_collection_router,
        )
        headers = admin_auth_headers(db_session)

        # 1. Admin tworzy firmę.
        create_response = client.post(
            ADMIN_WORK_CREATE, json={"company_name": "SPINETIME", "numeric": 1}, headers=headers
        )
        assert create_response.status_code == 201
        work_id = create_response.json()["data"]["id"]

        # 2. Dwa stanowiska pod firmą, w różnych datach.
        item1_response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work_id),
            json={
                "title": {"pl": "Junior Backend Developer", "en": "Junior Backend Developer"},
                "employment_type": "full_time",
                "date_from": "2024-04-01",
                "date_to": "2025-09-01",
                "skills": ["Django"],
            },
            headers=headers,
        )
        assert item1_response.status_code == 201
        item1_id = item1_response.json()["data"]["id"]

        item2_response = client.post(
            ADMIN_WORK_ITEM_CREATE.format(work_id=work_id),
            json={
                "title": {"pl": "Software Engineer", "en": "Software Engineer"},
                "employment_type": "full_time",
                "date_from": "2025-09-01",
                "skills": ["Django", "Redis"],
            },
            headers=headers,
        )
        assert item2_response.status_code == 201
        item2_id = item2_response.json()["data"]["id"]

        # 3. Logo firmy przez pełny cykl file domain: init -> upload -> confirm.
        init_response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "logo.png",
                "size": len(_IMAGE_BYTES),
                "directory": "work",
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
        client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)
        logo_response = client.put(ADMIN_WORK_LOGO.format(work_id=work_id), json={"file_id": file_id}, headers=headers)
        assert logo_response.status_code == 200

        # 4. Publiczna kolekcja, bez auth: firma, oba stanowiska posortowane
        #    date_from DESC (najnowsze pierwsze), logo widoczne.
        public_response = client.get(WORK_COLLECTION)
        assert public_response.status_code == 200
        [company] = [w for w in public_response.json()["data"] if w["id"] == work_id]
        assert company["logo_url"].startswith("/static/work/")
        assert [item["id"] for item in company["items"]] == [item2_id, item1_id]

        # 5. Admin edytuje firmę i jedno stanowisko — reszta nietknięta.
        update_work_response = client.put(
            ADMIN_WORK_UPDATE.format(work_id=work_id), json={"company_name": "SPINETIME Sp. z o.o."}, headers=headers
        )
        assert update_work_response.status_code == 200
        assert update_work_response.json()["data"]["company_name"] == "SPINETIME Sp. z o.o."

        update_item_response = client.put(
            ADMIN_WORK_ITEM_UPDATE.format(work_id=work_id, item_id=item2_id),
            json={"language_code": "en", "title": "Senior Software Engineer"},
            headers=headers,
        )
        assert update_item_response.status_code == 200
        assert update_item_response.json()["data"]["title"] == "Senior Software Engineer"

        # 6. Kasowanie jednego stanowiska.
        delete_item_response = client.delete(
            ADMIN_WORK_ITEM_DELETE.format(work_id=work_id, item_id=item1_id), headers=headers
        )
        assert delete_item_response.status_code == 200

        after_delete_item = client.get(WORK_COLLECTION)
        [company_after] = [w for w in after_delete_item.json()["data"] if w["id"] == work_id]
        assert len(company_after["items"]) == 1

        # 7. Kasowanie całej firmy usuwa logo z dysku i resztę stanowisk.
        saved_files = list((static_root / "work").iterdir())
        assert len(saved_files) == 1

        delete_work_response = client.delete(ADMIN_WORK_DELETE.format(work_id=work_id), headers=headers)
        assert delete_work_response.status_code == 200
        assert not saved_files[0].exists()

        final_response = client.get(WORK_COLLECTION)
        assert all(w["id"] != work_id for w in final_response.json()["data"])
