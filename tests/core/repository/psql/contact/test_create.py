from core.repository.psql.contact.create import create_contact_psql


class TestCreateContactPsql:
    def test_create01_returns_ok(self, db_session):
        result, err, ok = create_contact_psql(
            "Alice", "alice@example.com", "Question", None, "Hello there", db_session=db_session
        )

        assert ok is True and err is None
        assert result.name == "Alice" and result.is_read is False

    def test_create02_created_at_is_set(self, db_session):
        result, err, ok = create_contact_psql("Bob", "bob@example.com", None, None, "Hi", db_session=db_session)

        assert ok is True
        assert result.created_at is not None
