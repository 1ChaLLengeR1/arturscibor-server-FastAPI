from core.repository.psql.tools.create import create_tool_psql
from database.psql.models.tools import Tools


class TestCreateToolPsql:
    def test_create01_returns_ok(self, db_session):
        result, err, ok = create_tool_psql(
            {"pl": "Python", "en": "Python"},
            {"pl": "Język backendowy", "en": "Backend language"},
            80,
            1,
            "https://python.org",
            db_session=db_session,
        )

        assert ok is True and err is None
        assert result.id

    def test_create02_fields_match_input(self, db_session):
        result, _, ok = create_tool_psql(
            {"pl": "Rust", "en": "Rust"},
            {"pl": "Język systemowy", "en": "Systems language"},
            40,
            2,
            "https://rust-lang.org",
            db_session=db_session,
        )

        assert ok is True
        # Odpowiedź jest rozwiązana dla DEFAULT_LANGUAGE_CODE ("pl"), bo create_tool_psql
        # nie dostaje jawnego `lang` — patrz docs/7-i18n-section.md pkt. 6.
        assert result.name == "Rust"
        assert result.information == "Język systemowy"
        assert result.progress == 40
        assert result.numeric == 2
        assert result.link == "https://rust-lang.org"

    def test_create03_starts_with_no_images(self, db_session):
        result, _, ok = create_tool_psql({"pl": "Go", "en": "Go"}, None, None, None, None, db_session=db_session)

        assert ok is True
        assert result.images == []

    def test_create04_row_persisted(self, db_session):
        create_tool_psql({"pl": "Go", "en": "Go"}, None, None, None, None, db_session=db_session)

        assert db_session.query(Tools).count() == 1

    def test_create05_stores_full_jsonb_dict_for_both_languages(self, db_session):
        create_tool_psql(
            {"pl": "Python", "en": "Python (EN)"},
            {"pl": "Opis PL", "en": "Description EN"},
            None,
            None,
            None,
            db_session=db_session,
        )

        stored = db_session.query(Tools).one()
        assert stored.name == {"pl": "Python", "en": "Python (EN)"}
        assert stored.information == {"pl": "Opis PL", "en": "Description EN"}
