import uuid

from core.repository.psql.work.items.delete import delete_work_item_psql
from database.psql.models.work import WorkItem
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


class TestDeleteWorkItemPsql:
    def test_delete01_returns_ok(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        _, err, ok = delete_work_item_psql(str(work.id), str(item.id), db_session=db_session)

        assert ok is True and err is None

    def test_delete02_row_removed_from_db(self, db_session):
        work = create_test_work(db_session)
        item = create_test_work_item(db_session, work.id)

        delete_work_item_psql(str(work.id), str(item.id), db_session=db_session)

        assert db_session.query(WorkItem).filter(WorkItem.id == item.id).first() is None

    def test_delete03_nonexistent_returns_not_found(self, db_session):
        work = create_test_work(db_session)

        _, err, ok = delete_work_item_psql(str(work.id), str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_delete04_mismatched_work_id_returns_not_found(self, db_session):
        work = create_test_work(db_session)
        other_work = create_test_work(db_session, company_name="Other")
        item = create_test_work_item(db_session, work.id)

        _, err, ok = delete_work_item_psql(str(other_work.id), str(item.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
