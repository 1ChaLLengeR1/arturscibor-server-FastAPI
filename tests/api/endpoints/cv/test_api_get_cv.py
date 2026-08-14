import pytest

from api.endpoints.cv.get import router as cv_get_router
from api.endpoints.urls import CV
from config.settings import settings
from database.psql.models.file import FileType
from tests.api.endpoints.cv.helper import make_client
from tests.core.repository.psql.cv.helper import create_test_cv
from tests.core.repository.psql.file.helper import create_test_file

_PDF_BYTES = b"%PDF-1.4 fake pdf content for tests"


@pytest.fixture
def static_root(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "static_root", tmp_path)
    return tmp_path


def _write_cv_file(static_root, directory: str, name: str) -> None:
    file_dir = static_root / directory
    file_dir.mkdir(parents=True, exist_ok=True)
    (file_dir / name).write_bytes(_PDF_BYTES)


class TestApiGetCv:
    def test_get01_returns_404_when_not_seeded(self, db_session):
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 404

    def test_get02_returns_404_when_no_file_uploaded(self, db_session):
        create_test_cv(db_session)
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 404
        assert response.json()["data"]["key_type_error"] == "NotFound"

    def test_get03_returns_file_when_uploaded(self, db_session, static_root):
        file = create_test_file(
            db_session,
            file_type=FileType.DOCUMENT,
            original_name="cv.pdf",
            directory="cv",
            mime_type="application/pdf",
        )
        _write_cv_file(static_root, file.directory, file.name)
        create_test_cv(db_session, file_id=str(file.id))
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 200
        assert response.content == _PDF_BYTES
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="cv.pdf"' in response.headers["content-disposition"]

    def test_get04_returns_404_when_missing_on_disk(self, db_session, static_root):
        file = create_test_file(
            db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf", directory="cv", mime_type="application/pdf"
        )
        create_test_cv(db_session, file_id=str(file.id))
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 404
        assert response.json()["data"]["key_type_error"] == "MissingOnDisk"

    def test_get05_no_auth_required(self, db_session, static_root):
        file = create_test_file(
            db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf", directory="cv", mime_type="application/pdf"
        )
        _write_cv_file(static_root, file.directory, file.name)
        create_test_cv(db_session, file_id=str(file.id))
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 200
