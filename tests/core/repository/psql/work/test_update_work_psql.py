import uuid

from core.repository.psql.work.update import update_work_psql
from tests.core.repository.psql.work.helper import create_test_work


class TestUpdateWorkPsql:
    def test_update01_returns_ok(self, db_session):
        work = create_test_work(db_session, company_name="Old Name")

        result, err, ok = update_work_psql(str(work.id), company_name="New Name", db_session=db_session)

        assert ok is True and err is None
        assert result.company_name == "New Name"

    def test_update02_omitted_fields_are_left_untouched(self, db_session):
        work = create_test_work(db_session, company_name="SPINETIME", numeric=1)

        result, _, ok = update_work_psql(str(work.id), numeric=5, db_session=db_session)

        assert ok is True
        assert result.company_name == "SPINETIME"
        assert result.numeric == 5

    def test_update03_empty_company_name_returns_error(self, db_session):
        work = create_test_work(db_session)

        _, err, ok = update_work_psql(str(work.id), company_name="", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "InvalidValue"

    def test_update04_nonexistent_returns_not_found(self, db_session):
        _, err, ok = update_work_psql(str(uuid.uuid4()), company_name="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
