import uuid
from pathlib import Path

import pytest

import core.service.file.upload as upload_module
from config.settings import settings
from core.service.file.upload import upload_file_service
from database.psql.models.file import FileStatus
from tests.core.repository.psql.file.helper import create_test_file

_TEST_IMAGE = Path(__file__).resolve().parents[3] / "files_for_tests" / "Patryk, fortnite,naruto.png"
_IMAGE_BYTES = _TEST_IMAGE.read_bytes()
_IMAGE_SIZE = len(_IMAGE_BYTES)
_IMAGE_MIME = "image/png"


@pytest.fixture(autouse=True)
def static_root(tmp_path, monkeypatch):
    """Uploady lecą do tmp — test nie zaśmieca realnego static/files/."""
    monkeypatch.setattr(settings, "static_root", tmp_path)
    return tmp_path


class TestUploadFileService:
    def test_upload01_successful_upload(self, db_session):
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME, directory="projects")

        result, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is True and err is None
        assert result.status == FileStatus.COMPLETED.value
        assert result.url == f"/static/projects/{file.name}"

    def test_upload02_bytes_land_on_disk(self, db_session, static_root):
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME, directory="projects")

        upload_file_service(file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session)

        saved = static_root / "projects" / file.name
        assert saved.is_file()
        assert saved.read_bytes() == _IMAGE_BYTES

    def test_upload03_nonexistent_file_returns_404(self, db_session):
        _, err, ok = upload_file_service(
            file_id=str(uuid.uuid4()), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_upload04_wrong_status_returns_error(self, db_session):
        file = create_test_file(
            db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME, status=FileStatus.COMPLETED
        )

        _, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "InvalidStatus"

    def test_upload05_mime_mismatch_returns_error(self, db_session):
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME)

        _, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type="image/gif", db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "MimeTypeMismatch"

    def test_upload06_octet_stream_is_accepted_as_generic(self, db_session):
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME, directory="projects")

        result, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type="application/octet-stream", db_session=db_session
        )

        assert ok is True and err is None
        assert result.status == FileStatus.COMPLETED.value

    def test_upload07_size_mismatch_returns_error(self, db_session):
        file = create_test_file(db_session, size=_IMAGE_SIZE + 1, mime_type=_IMAGE_MIME)

        _, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "SizeMismatch"

    def test_upload08_file_exceeding_max_size_returns_error(self, db_session, monkeypatch):
        monkeypatch.setattr(upload_module, "MAX_FILE_SIZE_BYTES", 10)
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME)

        _, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "FileTooLarge"

    def test_upload09_disallowed_directory_returns_error(self, db_session):
        file = create_test_file(db_session, size=_IMAGE_SIZE, mime_type=_IMAGE_MIME, directory="secret")

        _, err, ok = upload_file_service(
            file_id=str(file.id), body=_IMAGE_BYTES, content_type=_IMAGE_MIME, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "InvalidDirectory"
