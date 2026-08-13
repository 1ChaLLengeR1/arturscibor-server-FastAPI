from core.repository.psql.tools.create import create_tool_psql
from database.psql.models.tools import Tools


class TestCreateToolPsql:
    def test_create01_returns_ok(self, db_session):
        result, err, ok = create_tool_psql(
            "Python", "Backend language", 80, 1, "https://python.org", db_session=db_session
        )

        assert ok is True and err is None
        assert result.id

    def test_create02_fields_match_input(self, db_session):
        result, _, ok = create_tool_psql(
            "Rust", "Systems language", 40, 2, "https://rust-lang.org", db_session=db_session
        )

        assert ok is True
        assert result.name == "Rust"
        assert result.information == "Systems language"
        assert result.progress == 40
        assert result.numeric == 2
        assert result.link == "https://rust-lang.org"

    def test_create03_starts_with_no_images(self, db_session):
        result, _, ok = create_tool_psql("Go", None, None, None, None, db_session=db_session)

        assert ok is True
        assert result.images == []

    def test_create04_row_persisted(self, db_session):
        create_tool_psql("Go", None, None, None, None, db_session=db_session)

        assert db_session.query(Tools).count() == 1
