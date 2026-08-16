import uuid
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

import database.psql.database as database_module
from api.endpoints.admin.file.confirm import router as admin_file_confirm_router
from api.endpoints.admin.file.init import router as admin_file_init_router
from api.endpoints.admin.file.upload import router as admin_file_upload_router
from api.endpoints.admin.projects.delete import router as admin_projects_delete_router
from api.endpoints.admin.projects.images.attach import router as admin_projects_image_attach_router
from api.endpoints.urls import (
    ADMIN_FILE_CONFIRM,
    ADMIN_FILE_INIT,
    ADMIN_FILE_UPLOAD,
    ADMIN_PROJECTS_DELETE,
    ADMIN_PROJECTS_IMAGE_ATTACH,
)
from config.settings import settings
from core.common.jwt import create_access_token
from database.psql.models.projects import Projects
from tests.api.endpoints.projects.helper import admin_auth_headers, make_client
from tests.core.repository.psql.projects.helper import create_test_project
from tests.core.repository.psql.users.helper import create_test_user

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


class TestApiAdminDeleteProject:
    def test_delete01_returns_200(self, db_session):
        client = make_client(db_session, admin_projects_delete_router)
        project = create_test_project(db_session)

        response = client.delete(
            ADMIN_PROJECTS_DELETE.format(project_id=project.id), headers=admin_auth_headers(db_session)
        )

        assert response.status_code == 200

    def test_delete02_row_removed_from_db(self, db_session):
        client = make_client(db_session, admin_projects_delete_router)
        project = create_test_project(db_session)

        client.delete(ADMIN_PROJECTS_DELETE.format(project_id=project.id), headers=admin_auth_headers(db_session))

        assert db_session.query(Projects).filter(Projects.id == project.id).first() is None

    def test_delete03_removes_attached_files_from_disk(self, db_session, static_root):
        client = make_client(
            db_session,
            admin_file_init_router,
            admin_file_upload_router,
            admin_file_confirm_router,
            admin_projects_image_attach_router,
            admin_projects_delete_router,
        )
        headers = admin_auth_headers(db_session)
        project = create_test_project(db_session)

        init_response = client.post(
            ADMIN_FILE_INIT,
            json={
                "original_name": "naruto.png",
                "size": len(_IMAGE_BYTES),
                "directory": "projects",
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
        client.post(
            ADMIN_PROJECTS_IMAGE_ATTACH.format(project_id=project.id), json={"file_id": file_id}, headers=headers
        )
        saved = next((static_root / "projects").iterdir())
        assert saved.is_file()

        response = client.delete(ADMIN_PROJECTS_DELETE.format(project_id=project.id), headers=headers)

        assert response.status_code == 200
        assert not saved.exists()

    def test_delete04_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, admin_projects_delete_router)

        response = client.delete(
            ADMIN_PROJECTS_DELETE.format(project_id=uuid.uuid4()), headers=admin_auth_headers(db_session)
        )

        assert response.status_code == 404

    def test_delete05_unauthenticated_returns_401(self, db_session):
        client = make_client(db_session, admin_projects_delete_router)
        project = create_test_project(db_session)

        response = client.delete(ADMIN_PROJECTS_DELETE.format(project_id=project.id))

        assert response.status_code == 401

    def test_delete06_non_admin_returns_403(self, db_session):
        client = make_client(db_session, admin_projects_delete_router)
        project = create_test_project(db_session)
        guest = create_test_user(db_session, type="guest")
        db_session.commit()
        token = create_access_token(str(guest.id))

        response = client.delete(
            ADMIN_PROJECTS_DELETE.format(project_id=project.id), headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
