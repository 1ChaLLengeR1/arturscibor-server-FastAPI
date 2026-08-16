from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.projects.create import router as admin_projects_create_router
from api.endpoints.admin.projects.delete import router as admin_projects_delete_router
from api.endpoints.admin.projects.images.attach import router as admin_projects_image_attach_router
from api.endpoints.admin.projects.images.detach import router as admin_projects_image_detach_router
from api.endpoints.admin.projects.update import router as admin_projects_update_router
from api.endpoints.projects.collection import router as projects_collection_router
from api.endpoints.projects.one import router as projects_one_router
from api.endpoints.urls import (
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
    ADMIN_PROJECTS_CREATE,
    ADMIN_PROJECTS_DELETE,
    ADMIN_PROJECTS_IMAGE_ATTACH,
    ADMIN_PROJECTS_IMAGE_DETACH,
    ADMIN_PROJECTS_UPDATE,
    PROJECTS_COLLECTION,
    PROJECTS_ONE,
)
from config.settings import settings
from tests.api.endpoints.projects.helper import admin_auth_headers, make_client

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


def _init_upload_confirm(client, headers, *, original_name: str) -> str:
    """Pełny cykl file domain: init -> upload -> confirm, zwraca file_id."""
    init_response = client.post(
        ADMIN_FILE_INIT,
        json={
            "original_name": original_name,
            "size": len(_IMAGE_BYTES),
            "directory": "projects",
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
    assert upload_response.json()["data"]["status"] == "completed"

    confirm_response = client.patch(ADMIN_FILE_CONFIRM.format(file_id=file_id), headers=headers)
    assert confirm_response.status_code == 200
    assert confirm_response.json()["data"]["status"] == "confirmed"

    return file_id


class TestProjectsE2E:
    def test_e2e01_create_project_attach_two_images_update_detach_delete(self, db_session, static_root):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_projects_create_router,
            admin_projects_update_router,
            admin_projects_delete_router,
            admin_projects_image_attach_router,
            admin_projects_image_detach_router,
            projects_collection_router,
            projects_one_router,
        )
        headers = admin_auth_headers(db_session)

        # 1. Admin tworzy projekt — bez zdjęć.
        create_response = client.post(
            ADMIN_PROJECTS_CREATE,
            json={
                "name": "Portfolio API",
                "short_description": {"pl": "Krótki opis", "en": "Short description"},
                "description": {"pl": "Długi opis projektu", "en": "Long project description"},
                "level": "advanced",
                "technologies": ["Python", "FastAPI", "PostgreSQL"],
                "github_url": "https://github.com/example/portfolio",
                "live_url": "https://example.com",
                "numeric": 1,
            },
            headers=headers,
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["data"]["id"]
        assert create_response.json()["data"]["images"] == []

        # 2. Dwa pliki przez pełny flow file domain: init -> upload -> confirm.
        first_file_id = _init_upload_confirm(client, headers, original_name="naruto-1.png")
        second_file_id = _init_upload_confirm(client, headers, original_name="naruto-2.png")

        # 3. Podpięcie obu pod projekt, w kolejności.
        attach_first = client.post(
            ADMIN_PROJECTS_IMAGE_ATTACH.format(project_id=project_id), json={"file_id": first_file_id}, headers=headers
        )
        assert attach_first.status_code == 200
        attach_second = client.post(
            ADMIN_PROJECTS_IMAGE_ATTACH.format(project_id=project_id), json={"file_id": second_file_id}, headers=headers
        )
        assert attach_second.status_code == 200
        images = attach_second.json()["data"]["images"]
        assert [image["file_id"] for image in images] == [first_file_id, second_file_id]
        assert all(image["url"].startswith("/static/projects/") for image in images)

        # 4. Publiczna kolekcja widzi projekt z obydwoma zdjęciami, bez auth.
        collection_response = client.get(PROJECTS_COLLECTION)
        assert collection_response.status_code == 200
        [project_in_collection] = [p for p in collection_response.json()["data"] if p["id"] == project_id]
        assert len(project_in_collection["images"]) == 2

        # 5. Publiczny szczegół widzi ten sam projekt z pełnym opisem, bez auth.
        one_response = client.get(PROJECTS_ONE.format(project_id=project_id))
        assert one_response.status_code == 200
        assert one_response.json()["data"]["description"] == "Długi opis projektu"
        assert len(one_response.json()["data"]["images"]) == 2

        # 6. Admin edytuje metadane projektu — zdjęcia mają zostać nietknięte.
        update_response = client.put(
            ADMIN_PROJECTS_UPDATE.format(project_id=project_id),
            json={"name": "Portfolio API v2", "level": "expert"},
            headers=headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["name"] == "Portfolio API v2"
        assert update_response.json()["data"]["level"] == "expert"
        assert len(update_response.json()["data"]["images"]) == 2

        # 7. Odpięcie jednego zdjęcia kasuje je fizycznie z dysku i z listy.
        first_saved_path = static_root / "projects" / _file_name_from_url(images[0]["url"])
        assert first_saved_path.is_file()
        detach_response = client.delete(
            ADMIN_PROJECTS_IMAGE_DETACH.format(project_id=project_id, file_id=first_file_id), headers=headers
        )
        assert detach_response.status_code == 200
        assert [image["file_id"] for image in detach_response.json()["data"]["images"]] == [second_file_id]
        assert not first_saved_path.exists()

        # 8. Kasowanie projektu usuwa też pozostały podpięty plik z dysku.
        second_saved_path = static_root / "projects" / _file_name_from_url(images[1]["url"])
        assert second_saved_path.is_file()
        delete_response = client.delete(ADMIN_PROJECTS_DELETE.format(project_id=project_id), headers=headers)
        assert delete_response.status_code == 200
        assert not second_saved_path.exists()

        final_collection = client.get(PROJECTS_COLLECTION)
        assert all(p["id"] != project_id for p in final_collection.json()["data"])
        final_one = client.get(PROJECTS_ONE.format(project_id=project_id))
        assert final_one.status_code == 404


def _file_name_from_url(url: str) -> str:
    return url.rsplit("/", 1)[-1]
