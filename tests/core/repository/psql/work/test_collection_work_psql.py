from core.repository.psql.work.collection import collection_work_psql
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


class TestCollectionWorkPsql:
    def test_collection01_empty_returns_empty_list(self, db_session):
        result, err, ok = collection_work_psql(db_session=db_session)

        assert ok is True and err is None
        assert result == []

    def test_collection02_returns_all_companies(self, db_session):
        create_test_work(db_session, company_name="SPINETIME", numeric=1)
        create_test_work(db_session, company_name="e-ux.pro", numeric=2)

        result, _, ok = collection_work_psql(db_session=db_session)

        assert ok is True
        assert len(result) == 2

    def test_collection03_ordered_by_numeric_ascending(self, db_session):
        create_test_work(db_session, company_name="Second", numeric=2)
        create_test_work(db_session, company_name="First", numeric=1)

        result, _, ok = collection_work_psql(db_session=db_session)

        assert ok is True
        assert [w.company_name for w in result] == ["First", "Second"]

    def test_collection04_null_numeric_sorted_last(self, db_session):
        create_test_work(db_session, company_name="NoOrder", numeric=None)
        create_test_work(db_session, company_name="First", numeric=1)

        result, _, ok = collection_work_psql(db_session=db_session)

        assert ok is True
        assert [w.company_name for w in result] == ["First", "NoOrder"]

    def test_collection05_includes_items_per_company(self, db_session):
        work = create_test_work(db_session)
        create_test_work_item(db_session, work.id)

        result, _, ok = collection_work_psql(db_session=db_session)

        assert ok is True
        assert len(result[0].items) == 1
