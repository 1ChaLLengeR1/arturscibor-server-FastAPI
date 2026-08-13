import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.tools.images.attach import router as admin_tools_image_attach_router
from api.endpoints.admin.tools.images.detach import router as admin_tools_image_detach_router
from api.endpoints.urls import (
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
    ADMIN_TOOLS_IMAGE_ATTACH,
    ADMIN_TOOLS_IMAGE_DETACH,
)
from config.settings import settings
from core.common.jwt import create_access_token
from database.psql.models.file import File
from tests.api.endpoints.tools.helper import admin_auth_headers, make_client
from tests.core.repository.psql.tools.helper import create_test_tool
from tests.core.repository.psql.users.helper import create_test_user

_TEST_IMAGE = Path(__file__).resolve().parents[4] / "files_for_tests" / "Patryk, fortnite,naruto.png"
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


def _attach_new_confirmed_file(client, headers, tool_id) -> str:
    init_response = client.post(
        ADMIN_FILE_INIT,
        json={
            "original_name": "naruto.png",
            "size": len(_IMAGE_BYTES),
            "directory": "tools",
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
    client.post(ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool_id), json={"file_id": file_id}, headers=headers)
    return file_id


def _all_routers():
    return (
        admin_file_init_router,
        admin_file_upload_router,
        admin_file_confirm_router,
        admin_tools_image_attach_router,
        admin_tools_image_detach_router,
    )


class TestApiAdminDetachToolImage:
    def test_detach01_returns_200_and_removes_from_response(self, db_session):
        client = make_client(db_session, *_all_routers())
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)
        file_id = _attach_new_confirmed_file(client, headers, tool.id)

        response = client.delete(
            ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool.id, file_id=file_id), headers=headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["images"] == []

    def test_detach02_deletes_file_row_and_disk_bytes(self, db_session, static_root):
        client = make_client(db_session, *_all_routers())
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)
        file_id = _attach_new_confirmed_file(client, headers, tool.id)
        saved = next((static_root / "tools").iterdir())
        assert saved.is_file()

        client.delete(ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool.id, file_id=file_id), headers=headers)

        assert not saved.exists()
        assert db_session.query(File).filter(File.id == file_id).first() is None

    def test_detach03_not_attached_returns_404(self, db_session):
        client = make_client(db_session, admin_tools_image_detach_router)
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)

        response = client.delete(
            ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool.id, file_id=uuid.uuid4()), headers=headers
        )

        assert response.status_code == 404

    def test_detach04_nonexistent_tool_returns_404(self, db_session):
        client = make_client(db_session, admin_tools_image_detach_router)
        headers = admin_auth_headers(db_session)

        response = client.delete(
            ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=uuid.uuid4(), file_id=uuid.uuid4()), headers=headers
        )

        assert response.status_code == 404

    def test_detach05_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_tools_image_detach_router)
        tool = create_test_tool(db_session)

        response = client.delete(ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool.id, file_id=uuid.uuid4()))

        assert response.status_code == 401

    def test_detach06_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_tools_image_detach_router)
        tool = create_test_tool(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.delete(
            ADMIN_TOOLS_IMAGE_DETACH.format(tool_id=tool.id, file_id=uuid.uuid4()),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
