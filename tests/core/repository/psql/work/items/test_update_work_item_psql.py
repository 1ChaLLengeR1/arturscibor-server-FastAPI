import uuid

from core.repository.psql.work.items.update import update_work_item_psql
from database.psql.models.work import EmploymentType
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


class TestUpdateWorkItemPsql:
    def test_update01_returns_ok(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        result, err, ok = update_work_item_psql(
            str(work.id), str(item.id), title="Updated Title", db_session=db_session
        )

        assert ok is True and err is None
        assert result.title == "Updated Title"

    def test_update02_omitted_fields_are_left_untouched(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id, employment_type=EmploymentType.B2B)

        result, _, ok = update_work_item_psql(str(work.id), str(item.id), title="New Title", db_session=db_session)

        assert ok is True
        assert result.title == "New Title"
        assert result.employment_type == "b2b"

    def test_update03_translatable_field_clears_only_that_language(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(
            db_session, work.id, body_markdown={"pl": "Opis PL", "en": "Description EN"}
        )

        result, _, ok = update_work_item_psql(
            str(work.id), str(item.id), body_markdown=None, db_session=db_session
        )

        assert ok is True
        assert result.body_markdown is None
        assert item.body_markdown == {"en": "Description EN"}

    def test_update04_edits_one_language_without_touching_the_other(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id, title={"pl": "Programista", "en": "Developer"})

        result, _, ok = update_work_item_psql(
            str(work.id), str(item.id), language_code="en", title="Backend Developer", db_session=db_session
        )

        assert ok is True
        assert result.title == "Backend Developer"
        assert item.title["pl"] == "Programista"

    def test_update05_empty_title_returns_error(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        _, err, ok = update_work_item_psql(str(work.id), str(item.id), title="", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "InvalidValue"

    def test_update06_nonexistent_returns_not_found(self, db_session):
        work = create_test_work(db_session)

        _, err, ok = update_work_item_psql(str(work.id), str(uuid.uuid4()), title="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_update07_mismatched_work_id_returns_not_found(self, db_session):
        work = create_test_work(db_session)
        other_work = create_test_work(db_session, company_name="Other")
        item = create_test_work_item(db_session, work.id)

        _, err, ok = update_work_item_psql(str(other_work.id), str(item.id), title="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
