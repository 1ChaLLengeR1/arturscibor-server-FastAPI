import uuid

from core.repository.psql.file.update import update_file_by_id_psql
from database.psql.models.file import FileStatus
from tests.core.repository.psql.file.helper import create_test_file


class TestUpdateFileByIdPsql:
    def test_update01_returns_ok(self, db_session):
        file = create_test_file(db_session)

        result, err, ok = update_file_by_id_psql(
            file_id=str(file.id), status=FileStatus.COMPLETED, db_session=db_session
        )

        assert ok is True and err is None

    def test_update02_status_updated(self, db_session):
        file = create_test_file(db_session)

        result, _, ok = update_file_by_id_psql(file_id=str(file.id), status=FileStatus.COMPLETED, db_session=db_session)

        assert ok is True
        assert result.status == FileStatus.COMPLETED.value

    def test_update03_url_updated(self, db_session):
        file = create_test_file(db_session)

        result, _, ok = update_file_by_id_psql(
            file_id=str(file.id), url="/static/projects/uuid_photo.png", db_session=db_session
        )

        assert ok is True
        assert result.url == "/static/projects/uuid_photo.png"

    def test_update04_nonexistent_returns_not_found(self, db_session):
        result, err, ok = update_file_by_id_psql(
            file_id=str(uuid.uuid4()), status=FileStatus.COMPLETED, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "NotFound"
