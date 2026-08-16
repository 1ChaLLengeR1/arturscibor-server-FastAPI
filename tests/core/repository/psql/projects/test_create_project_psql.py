from datetime import date

from core.repository.psql.projects.create import create_project_psql
from database.psql.models.projects import ProjectLevel, Projects


class TestCreateProjectPsql:
    def test_create01_returns_ok(self, db_session):
        result, err, ok = create_project_psql(
            "Portfolio API",
            {"pl": "Krótki opis", "en": "Short description"},
            {"pl": "Długi opis", "en": "Long description"},
            ProjectLevel.ADVANCED,
            ["Python", "FastAPI"],
            "https://github.com/example/portfolio",
            "https://example.com",
            date(2026, 1, 15),
            1,
            db_session=db_session,
        )

        assert ok is True and err is None
        assert result.id

    def test_create02_fields_match_input(self, db_session):
        result, _, ok = create_project_psql(
            "Portfolio API",
            {"pl": "Krótki opis", "en": "Short description"},
            {"pl": "Długi opis", "en": "Long description"},
            ProjectLevel.ADVANCED,
            ["Python", "FastAPI"],
            "https://github.com/example/portfolio",
            "https://example.com",
            date(2026, 1, 15),
            2,
            db_session=db_session,
        )

        assert ok is True
        # Odpowiedź jest rozwiązana dla DEFAULT_LANGUAGE_CODE ("pl"), bo create_project_psql
        # nie dostaje jawnego `lang` — patrz docs/7-i18n-section.md pkt. 6.
        assert result.name == "Portfolio API"
        assert result.short_description == "Krótki opis"
        assert result.description == "Długi opis"
        assert result.level == "advanced"
        assert result.technologies == ["Python", "FastAPI"]
        assert result.github_url == "https://github.com/example/portfolio"
        assert result.live_url == "https://example.com"
        assert result.completed_at == date(2026, 1, 15)
        assert result.numeric == 2

    def test_create03_starts_with_no_images(self, db_session):
        result, _, ok = create_project_psql(
            "Empty", None, None, None, None, None, None, None, None, db_session=db_session
        )

        assert ok is True
        assert result.images == []

    def test_create04_row_persisted(self, db_session):
        create_project_psql("Empty", None, None, None, None, None, None, None, None, db_session=db_session)

        assert db_session.query(Projects).count() == 1

    def test_create05_stores_full_jsonb_dict_for_both_languages(self, db_session):
        create_project_psql(
            "Portfolio API",
            {"pl": "Opis PL", "en": "Description EN"},
            {"pl": "Długi PL", "en": "Long EN"},
            None,
            None,
            None,
            None,
            None,
            None,
            db_session=db_session,
        )

        stored = db_session.query(Projects).one()
        assert stored.short_description == {"pl": "Opis PL", "en": "Description EN"}
        assert stored.description == {"pl": "Długi PL", "en": "Long EN"}
