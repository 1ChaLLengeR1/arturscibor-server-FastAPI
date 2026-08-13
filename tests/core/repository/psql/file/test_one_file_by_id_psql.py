import uuid

from core.repository.psql.file.one import one_file_by_id_psql
from tests.core.repository.psql.file.helper import create_test_file


class TestOneFileByIdPsql:
    def test_one01_returns_file(self, db_session):
        file = create_test_file(db_session)

        result, err, ok = one_file_by_id_psql(file_id=str(file.id), db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(file.id)

    def test_one02_nonexistent_returns_not_found(self, db_session):
        result, err, ok = one_file_by_id_psql(file_id=str(uuid.uuid4()), db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"
