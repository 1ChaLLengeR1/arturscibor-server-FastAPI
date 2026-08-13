import uuid

from core.repository.psql.work.logo.update import set_work_logo_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.work.helper import create_test_work


class TestSetWorkLogoPsql:
    def test_set01_sets_logo(self, db_session):
        work = create_test_work(db_session)
        file = create_test_file(db_session)

        result, err, ok = set_work_logo_psql(str(work.id), str(file.id), db_session=db_session)

        assert ok is True and err is None
        assert result.logo_file_id == str(file.id)

    def test_set02_resolves_logo_url(self, db_session):
        work = create_test_work(db_session)
        file = create_test_file(db_session)
        file.url = "/static/work/logo.png"
        db_session.flush()

        result, _, ok = set_work_logo_psql(str(work.id), str(file.id), db_session=db_session)

        assert ok is True
        assert result.logo_url == "/static/work/logo.png"

    def test_set03_none_clears_logo(self, db_session):
        work = create_test_work(db_session)
        file = create_test_file(db_session)
        set_work_logo_psql(str(work.id), str(file.id), db_session=db_session)

        result, _, ok = set_work_logo_psql(str(work.id), None, db_session=db_session)

        assert ok is True
        assert result.logo_file_id is None
        assert result.logo_url is None

    def test_set04_nonexistent_work_returns_not_found(self, db_session):
        _, err, ok = set_work_logo_psql(str(uuid.uuid4()), None, db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
