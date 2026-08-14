import uuid
from datetime import date

from core.repository.psql.work.one import one_work_by_id_psql
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


class TestOneWorkByIdPsql:
    def test_one01_returns_work(self, db_session):
        work = create_test_work(db_session, company_name="SPINETIME")

        result, err, ok = one_work_by_id_psql(str(work.id), db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(work.id)
        assert result.company_name == "SPINETIME"

    def test_one02_no_items_returns_empty_list(self, db_session):
        work = create_test_work(db_session)

        result, _, ok = one_work_by_id_psql(str(work.id), db_session=db_session)

        assert ok is True
        assert result.items == []

    def test_one03_nonexistent_returns_not_found(self, db_session):
        result, err, ok = one_work_by_id_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"

    def test_one04_items_ordered_by_date_from_descending(self, db_session):
        work = create_test_work(db_session)
        older = create_test_work_item(
            db_session, work.id, title={"pl": "Junior Dev", "en": "Junior Dev"}, date_from=date(2023, 1, 1)
        )
        newer = create_test_work_item(
            db_session, work.id, title={"pl": "Senior Dev", "en": "Senior Dev"}, date_from=date(2025, 1, 1)
        )

        result, _, ok = one_work_by_id_psql(str(work.id), db_session=db_session)

        assert ok is True
        assert [item.id for item in result.items] == [str(newer.id), str(older.id)]

    def test_one05_resolves_item_title_for_requested_language(self, db_session):
        work = create_test_work(db_session)
        create_test_work_item(db_session, work.id, title={"pl": "Inżynier Oprogramowania", "en": "Software Engineer"})

        result, _, ok = one_work_by_id_psql(str(work.id), lang="en", db_session=db_session)

        assert ok is True
        assert result.items[0].title == "Software Engineer"

    def test_one06_falls_back_to_default_language_when_missing(self, db_session):
        work = create_test_work(db_session)
        create_test_work_item(db_session, work.id, title={"pl": "Inżynier Oprogramowania", "en": "Software Engineer"})

        result, _, ok = one_work_by_id_psql(str(work.id), lang="de", db_session=db_session)

        assert ok is True
        assert result.items[0].title == "Inżynier Oprogramowania"
