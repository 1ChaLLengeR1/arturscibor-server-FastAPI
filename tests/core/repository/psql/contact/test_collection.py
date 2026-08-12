from datetime import UTC, datetime, timedelta

from core.repository.psql.contact.collection import collection_contact_psql
from tests.core.repository.psql.contact.helper import create_test_contact


class TestCollectionContactPsql:
    def test_collection01_returns_ordered_newest_first(self, db_session):
        # created_at uses server_default=func.now(), which is transaction
        # start time in Postgres — not statement time — so two inserts in
        # the same uncommitted test transaction would otherwise get the
        # exact same timestamp. Set it explicitly instead of relying on
        # real-time gaps (a sleep() here wouldn't help at all).
        first = create_test_contact(db_session, name="First")
        second = create_test_contact(db_session, name="Second")
        first.created_at = datetime.now(UTC) - timedelta(minutes=1)
        second.created_at = datetime.now(UTC)
        db_session.flush()

        result, err, ok = collection_contact_psql(db_session=db_session)

        assert ok is True and err is None
        assert [c.name for c in result] == ["Second", "First"]

    def test_collection02_respects_limit(self, db_session):
        for i in range(3):
            create_test_contact(db_session, name=f"Contact {i}")

        result, err, ok = collection_contact_psql(limit=2, db_session=db_session)

        assert ok is True
        assert len(result) == 2

    def test_collection03_filters_by_is_read(self, db_session):
        create_test_contact(db_session, name="Unread")
        read = create_test_contact(db_session, name="Read")
        read.is_read = True
        db_session.flush()

        result, err, ok = collection_contact_psql(is_read=True, db_session=db_session)

        assert ok is True
        assert [c.id for c in result] == [str(read.id)]

    def test_collection04_filters_by_date_range(self, db_session):
        old = create_test_contact(db_session, name="Old")
        old.created_at = datetime.now(UTC) - timedelta(days=10)
        db_session.flush()
        create_test_contact(db_session, name="Recent")

        result, err, ok = collection_contact_psql(
            created_from=datetime.now(UTC) - timedelta(days=1), db_session=db_session
        )

        assert ok is True
        assert [c.name for c in result] == ["Recent"]
