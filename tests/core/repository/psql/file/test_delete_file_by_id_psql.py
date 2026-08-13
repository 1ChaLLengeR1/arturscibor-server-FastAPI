import uuid

from core.repository.psql.file.delete import delete_file_by_id_psql
from database.psql.models.file import File
from tests.core.repository.psql.file.helper import create_test_file


class TestDeleteFileByIdPsql:
    def test_delete01_returns_ok(self, db_session):
        file = create_test_file(db_session)

        result, err, ok = delete_file_by_id_psql(file_id=str(file.id), db_session=db_session)

        assert ok is True and err is None
        assert result.deleted is True

    def test_delete02_file_removed_from_db(self, db_session):
        file = create_test_file(db_session)

        delete_file_by_id_psql(file_id=str(file.id), db_session=db_session)

        assert db_session.query(File).filter(File.id == file.id).first() is None

    def test_delete03_response_has_directory_and_name(self, db_session):
        file = create_test_file(db_session, directory="tools", name="uuid_img.png")

        result, _, ok = delete_file_by_id_psql(file_id=str(file.id), db_session=db_session)

        assert ok is True
        assert result.directory == "tools"
        assert result.name == "uuid_img.png"

    def test_delete04_nonexistent_returns_not_found(self, db_session):
        result, err, ok = delete_file_by_id_psql(file_id=str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
