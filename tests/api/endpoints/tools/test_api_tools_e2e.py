from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.tools.create import router as admin_tools_create_router
from api.endpoints.admin.tools.delete import router as admin_tools_delete_router
from api.endpoints.admin.tools.images.attach import router as admin_tools_image_attach_router
from api.endpoints.admin.tools.images.detach import router as admin_tools_image_detach_router
from api.endpoints.admin.tools.update import router as admin_tools_update_router
from api.endpoints.tools.collection import router as tools_collection_router
from api.endpoints.urls import (
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
    ADMIN_TOOLS_CREATE,
    ADMIN_TOOLS_DELETE,
    ADMIN_TOOLS_IMAGE_ATTACH,
    ADMIN_TOOLS_IMAGE_DETACH,
    ADMIN_TOOLS_UPDATE,
    TOOLS_COLLECTION,
)
from config.settings import settings
from tests.api.endpoints.tools.helper import admin_auth_headers, make_client

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
            "directory": "tools",
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


class TestToolsE2E:
    def test_e2e01_create_tool_attach_two_images_update_detach_delete(self, db_session, static_root):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_tools_create_router,
            admin_tools_update_router,
            admin_tools_delete_router,
            admin_tools_image_attach_router,
            admin_tools_image_detach_router,
            tools_collection_router,
        )
        headers = admin_auth_headers(db_session)

        # 1. Admin tworzy tool — bez zdjęć.
        create_response = client.post(
            ADMIN_TOOLS_CREATE,
            json={"name": "Python", "information": "Backend language", "progress": 70, "numeric": 1},
            headers=headers,
        )
        assert create_response.status_code == 201
        tool_id = create_response.json()["data"]["id"]
        assert create_response.json()["data"]["images"] == []

        # 2. Dwa pliki przez pełny flow file domain: init -> upload -> confirm.
        first_file_id = _init_upload_confirm(client, headers, original_name="naruto-1.png")
        second_file_id = _init_upload_confirm(client, headers, original_name="naruto-2.png")

        # 3. Podpięcie obu pod tool, w kolejności.
        attach_first = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool_id), json={"file_id": first_file_id}, headers=headers
        )
        assert attach_first.status_code == 200
        attach_second = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool_id), json={"file_id": second_file_id}, headers=headers
        )
        assert attach_second.status_code == 200
        images = attach_second.json()["data"]["images"]
        assert [image["file_id"] for image in images] == [first_file_id, second_file_id]
        assert all(image["url"].startswith("/static/tools/") for image in images)

        # 4. Publiczna kolekcja widzi tool z obydwoma zdjęciami, bez auth.
        collection_response = client.get(TOOLS_COLLECTION)
        assert collection_response.status_code == 200
        [tool_in_collection] = [t for t in collection_response.json()["data"] if t["id"] == tool_id]
        assert len(tool_in_collection["images"]) == 2

        # 5. Admin edytuje metadane toola — zdjęcia mają zostać nietknięte.
        update_response = client.put(
            ADMIN_TOOLS_UPDATE.format(tool_id=tool_id),
            json={"name": "Python 3", "progress": 90},
            headers=headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["name"] == "Python 3"
        assert update_response.json()["data"]["progress"] == 90
        assert len(update_response.json()["data"]["images"]) == 2

        # 6. Odpięcie jednego zdjęcia kasuje je fizycznie z dysku i z listy.
        first_saved_path = static_root / "tools" / _file_name_from_url(images[0]["url"])
        assert first_saved_path.is_file()
        detach_response = client.delete(
            ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool_id, file_id=first_file_id), headers=headers
        )
        assert detach_response.status_code == 200
        assert [image["file_id"] for image in detach_response.json()["data"]["images"]] == [second_file_id]
        assert not first_saved_path.exists()

        # 7. Kasowanie toola usuwa też pozostały podpięty plik z dysku.
        second_saved_path = static_root / "tools" / _file_name_from_url(images[1]["url"])
        assert second_saved_path.is_file()
        delete_response = client.delete(ADMIN_TOOLS_DELETE.format(tool_id=tool_id), headers=headers)
        assert delete_response.status_code == 200
        assert not second_saved_path.exists()

        final_collection = client.get(TOOLS_COLLECTION)
        assert all(t["id"] != tool_id for t in final_collection.json()["data"])


def _file_name_from_url(url: str) -> str:
    return url.rsplit("/", 1)[-1]
