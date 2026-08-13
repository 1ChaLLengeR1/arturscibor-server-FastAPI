import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.tools.images.attach import router as admin_tools_image_attach_router
from api.endpoints.urls import ADMIN_FILE_CONFIRM, ADMIN_FILE_INIT, ADMIN_FILE_UPLOAD, ADMIN_TOOLS_IMAGE_ATTACH
from config.settings import settings
from core.common.jwt import create_access_token
from tests.api.endpoints.tools.helper import admin_auth_headers, make_client
from tests.core.repository.psql.file.helper import create_test_file
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


def _confirmed_file_id(client, headers, *, directory: str = "tools") -> str:
    init_response = client.post(
        ADMIN_FILE_INIT,
        json={
            "original_name": "naruto.png",
            "size": len(_IMAGE_BYTES),
            "directory": directory,
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
    return file_id


class TestApiAdminAttachToolImage:
    def test_attach01_returns_200_with_image_in_response(self, db_session):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_confirm_router,
            admin_tools_image_attach_router,
        )
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)
        file_id = _confirmed_file_id(client, headers)

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id), json={"file_id": file_id}, headers=headers
        )

        assert response.status_code == 200
        images = response.json()["data"]["images"]
        assert len(images) == 1
        assert images[0]["file_id"] == file_id
        assert images[0]["url"].startswith("/static/tools/")

    def test_attach02_pending_file_returns_400(self, db_session):
        client = make_client(db_session, admin_tools_image_attach_router)
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)
        file = create_test_file(db_session)

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id), json={"file_id": str(file.id)}, headers=headers
        )

        assert response.status_code == 400
        assert response.json()["data"]["key_type_error"] == "InvalidStatus"

    def test_attach03_nonexistent_tool_returns_404(self, db_session):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_confirm_router,
            admin_tools_image_attach_router,
        )
        headers = admin_auth_headers(db_session)
        file_id = _confirmed_file_id(client, headers)

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=uuid.uuid4()), json={"file_id": file_id}, headers=headers
        )

        assert response.status_code == 404

    def test_attach04_nonexistent_file_returns_404(self, db_session):
        client = make_client(db_session, admin_tools_image_attach_router)
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id), json={"file_id": str(uuid.uuid4())}, headers=headers
        )

        assert response.status_code == 404

    def test_attach05_already_attached_returns_409(self, db_session):
        client = make_client(
            db_session, admin_file_init_router, admin_file_upload_router, admin_file_confirm_router,
            admin_tools_image_attach_router,
        )
        headers = admin_auth_headers(db_session)
        tool = create_test_tool(db_session)
        other_tool = create_test_tool(db_session, name={"pl": "Other", "en": "Other"})
        file_id = _confirmed_file_id(client, headers)
        client.post(ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id), json={"file_id": file_id}, headers=headers)

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=other_tool.id), json={"file_id": file_id}, headers=headers
        )

        assert response.status_code == 409
        assert response.json()["data"]["key_type_error"] == "AlreadyAttached"

    def test_attach06_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_tools_image_attach_router)
        tool = create_test_tool(db_session)

        response = client.post(ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id), json={"file_id": str(uuid.uuid4())})

        assert response.status_code == 401

    def test_attach07_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_tools_image_attach_router)
        tool = create_test_tool(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.post(
            ADMIN_TOOLS_IMAGE_ATTACH.format(tool_id=tool.id),
            json={"file_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
