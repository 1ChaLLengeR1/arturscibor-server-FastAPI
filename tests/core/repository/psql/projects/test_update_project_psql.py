import uuid
from datetime import date

from core.repository.psql.projects.images.attach import attach_project_image_psql
from core.repository.psql.projects.one import one_project_by_id_psql
from core.repository.psql.projects.update import update_project_psql
from database.psql.models.projects import ProjectLevel
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.projects.helper import create_test_project


class TestUpdateProjectPsql:
    def test_update01_returns_ok(self, db_session):
        project = create_test_project(db_session)

        result, err, ok = update_project_psql(str(project.id), name="Updated", db_session=db_session)

        assert ok is True and err is None
        assert result.name == "Updated"

    def test_update02_omitted_fields_are_left_untouched(self, db_session):
        project = create_test_project(
            db_session,
            name="Portfolio API",
            description={"pl": "Opis", "en": "Description"},
            level=ProjectLevel.ADVANCED,
        )

        result, _, ok = update_project_psql(str(project.id), name="Portfolio API v2", db_session=db_session)

        assert ok is True
        assert result.name == "Portfolio API v2"
        assert result.description == "Opis"
        assert result.level == "advanced"

    def test_update03_explicit_none_clears_only_that_language(self, db_session):
        project = create_test_project(db_session, description={"pl": "Opis PL", "en": "Description EN"})

        result, _, ok = update_project_psql(str(project.id), description=None, db_session=db_session)

        assert ok is True
        assert result.description is None  # pl (domyślny język) wyczyszczony — nic do pokazania
        assert project.description == {"en": "Description EN"}  # en zostaje nietknięte w JSONB

    def test_update04_name_cannot_be_cleared(self, db_session):
        project = create_test_project(db_session)

        _, err, ok = update_project_psql(str(project.id), name=None, db_session=db_session)

        assert ok is False
        assert err.key_type_error == "InvalidValue"

    def test_update05_edits_one_language_without_touching_the_other(self, db_session):
        project = create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"})

        result, _, ok = update_project_psql(
            str(project.id), language_code="en", short_description="Python Snake", db_session=db_session
        )

        assert ok is True
        assert result.short_description == "Python Snake"  # odpowiedź rozwiązana dla edytowanego języka (en)
        pl_view, _, _ = one_project_by_id_psql(str(project.id), lang="pl", db_session=db_session)
        assert pl_view.short_description == "Wąż"  # pl bez zmian

    def test_update06_keeps_attached_images_in_response(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)
        attach_project_image_psql(str(project.id), str(file.id), sort_order=0, db_session=db_session)

        result, _, ok = update_project_psql(str(project.id), name="Updated", db_session=db_session)

        assert ok is True
        assert len(result.images) == 1
        assert result.images[0].file_id == str(file.id)

    def test_update07_nonexistent_returns_not_found(self, db_session):
        result, err, ok = update_project_psql(str(uuid.uuid4()), name="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_update08_technologies_full_replace(self, db_session):
        project = create_test_project(db_session, technologies=["Python", "FastAPI"])

        result, _, ok = update_project_psql(
            str(project.id), technologies=["Rust", "Postgres"], db_session=db_session
        )

        assert ok is True
        assert result.technologies == ["Rust", "Postgres"]

    def test_update09_updates_level_github_live_and_completed_at(self, db_session):
        project = create_test_project(db_session, level=ProjectLevel.BEGINNER)

        result, _, ok = update_project_psql(
            str(project.id),
            level=ProjectLevel.EXPERT,
            github_url="https://github.com/example/repo",
            live_url="https://example.com",
            completed_at=date(2026, 3, 1),
            numeric=5,
            db_session=db_session,
        )

        assert ok is True
        assert result.level == "expert"
        assert result.github_url == "https://github.com/example/repo"
        assert result.live_url == "https://example.com"
        assert result.completed_at == date(2026, 3, 1)
        assert result.numeric == 5
