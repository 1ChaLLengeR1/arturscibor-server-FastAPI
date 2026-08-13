from core.repository.psql.work.create import create_work_psql
from database.psql.models.work import Work


class TestCreateWorkPsql:
    def test_create01_returns_ok(self, db_session):
        result, err, ok = create_work_psql("SPINETIME", 1, db_session=db_session)

        assert ok is True and err is None
        assert result.id

    def test_create02_fields_match_input(self, db_session):
        result, _, ok = create_work_psql("e-ux.pro", 2, db_session=db_session)

        assert ok is True
        assert result.company_name == "e-ux.pro"
        assert result.numeric == 2

    def test_create03_starts_with_no_items_and_no_logo(self, db_session):
        result, _, ok = create_work_psql("SPINETIME", None, db_session=db_session)

        assert ok is True
        assert result.items == []
        assert result.logo_file_id is None
        assert result.logo_url is None

    def test_create04_row_persisted(self, db_session):
        create_work_psql("SPINETIME", None, db_session=db_session)

        assert db_session.query(Work).count() == 1
