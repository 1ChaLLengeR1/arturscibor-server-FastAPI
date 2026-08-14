from datetime import date

from core.repository.psql.work.items.create import create_work_item_psql
from database.psql.models.work import EmploymentType, WorkItem
from tests.core.repository.psql.work.helper import create_test_work


class TestCreateWorkItemPsql:
    def test_create01_returns_ok(self, db_session):
        work = create_test_work(db_session)

        result, err, ok = create_work_item_psql(
            str(work.id),
            {"pl": "Inżynier Oprogramowania", "en": "Software Engineer"},
            EmploymentType.FULL_TIME,
            None,
            date(2025, 9, 1),
            None,
            None,
            ["Django", "Redis"],
            db_session=db_session,
        )

        assert ok is True and err is None
        assert result.id

    def test_create02_fields_match_input(self, db_session):
        work = create_test_work(db_session)

        result, _, ok = create_work_item_psql(
            str(work.id),
            {"pl": "Programista", "en": "Developer"},
            EmploymentType.B2B,
            {"pl": "Wrocław", "en": "Wroclaw"},
            date(2024, 1, 1),
            date(2024, 12, 31),
            {"pl": "Opis", "en": "Description"},
            ["Vue.js"],
            db_session=db_session,
        )

        assert ok is True
        assert result.title == "Programista"
        assert result.employment_type == "b2b"
        assert result.location == "Wrocław"
        assert result.date_from == date(2024, 1, 1)
        assert result.date_to == date(2024, 12, 31)
        assert result.body_markdown == "Opis"
        assert result.skills == ["Vue.js"]

    def test_create03_row_persisted(self, db_session):
        work = create_test_work(db_session)

        create_work_item_psql(
            str(work.id), {"pl": "Dev", "en": "Dev"}, None, None, None, None, None, None, db_session=db_session
        )

        assert db_session.query(WorkItem).count() == 1
