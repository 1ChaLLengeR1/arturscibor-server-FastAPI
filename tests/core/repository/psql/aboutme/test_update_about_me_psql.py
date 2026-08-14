from core.repository.psql.aboutme.images.attach import attach_about_me_image_psql
from core.repository.psql.aboutme.one import one_about_me_psql
from core.repository.psql.aboutme.update import update_about_me_psql
from tests.core.repository.psql.aboutme.helper import create_test_about_me
from tests.core.repository.psql.file.helper import create_test_file


class TestUpdateAboutMePsql:
    def test_update01_returns_ok(self, db_session):
        create_test_about_me(db_session, name="Old Name")

        result, err, ok = update_about_me_psql(name="New Name", db_session=db_session)

        assert ok is True and err is None
        assert result.name == "New Name"

    def test_update02_omitted_fields_are_left_untouched(self, db_session):
        create_test_about_me(
            db_session,
            name="Artur Ścibor",
            job_title={"pl": "Programista", "en": "Developer"},
        )

        result, _, ok = update_about_me_psql(name="Updated Name", db_session=db_session)

        assert ok is True
        assert result.name == "Updated Name"
        assert result.job_title == "Programista"

    def test_update03_translatable_field_clears_only_that_language(self, db_session):
        create_test_about_me(db_session, body_markdown={"pl": "Opis PL", "en": "Description EN"})

        result, _, ok = update_about_me_psql(body_markdown=None, db_session=db_session)

        assert ok is True
        assert result.body_markdown is None  # pl (domyślny język) wyczyszczony

        pl_row, _, _ = one_about_me_psql(db_session=db_session)
        en_row, _, _ = one_about_me_psql(lang="en", db_session=db_session)
        assert pl_row.body_markdown is None
        assert en_row.body_markdown == "Description EN"  # en zostaje nietknięte w JSONB

    def test_update04_edits_one_language_without_touching_the_other(self, db_session):
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})

        result, _, ok = update_about_me_psql(language_code="en", job_title="Backend Developer", db_session=db_session)

        assert ok is True
        assert result.job_title == "Backend Developer"
        pl_view, _, _ = one_about_me_psql(lang="pl", db_session=db_session)
        assert pl_view.job_title == "Programista"

    def test_update05_keeps_attached_images_in_response(self, db_session):
        about_me = create_test_about_me(db_session)
        file = create_test_file(db_session)
        attach_about_me_image_psql(str(about_me.id), str(file.id), sort_order=0, db_session=db_session)

        result, _, ok = update_about_me_psql(name="Updated", db_session=db_session)

        assert ok is True
        assert len(result.images) == 1
        assert result.images[0].file_id == str(file.id)

    def test_update06_not_seeded_returns_not_found(self, db_session):
        result, err, ok = update_about_me_psql(name="X", db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
