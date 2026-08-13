from core.repository.psql.aboutme.images.attach import attach_about_me_image_psql
from core.repository.psql.aboutme.one import one_about_me_psql
from tests.core.repository.psql.aboutme.helper import create_test_about_me
from tests.core.repository.psql.file.helper import create_test_file


class TestOneAboutMePsql:
    def test_one01_returns_seeded_row(self, db_session):
        about_me = create_test_about_me(db_session, name="Artur Ścibor")

        result, err, ok = one_about_me_psql(db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(about_me.id)
        assert result.name == "Artur Ścibor"

    def test_one02_not_seeded_returns_not_found(self, db_session):
        result, err, ok = one_about_me_psql(db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"

    def test_one03_no_images_returns_empty_list(self, db_session):
        create_test_about_me(db_session)

        result, _, ok = one_about_me_psql(db_session=db_session)

        assert ok is True
        assert result.images == []

    def test_one04_resolves_requested_language(self, db_session):
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})

        result, _, ok = one_about_me_psql(lang="en", db_session=db_session)

        assert ok is True
        assert result.job_title == "Developer"

    def test_one05_falls_back_to_default_language_when_missing(self, db_session):
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})

        result, _, ok = one_about_me_psql(lang="de", db_session=db_session)

        assert ok is True
        assert result.job_title == "Programista"

    def test_one06_returns_attached_images_ordered_by_sort_order(self, db_session):
        about_me = create_test_about_me(db_session)
        second = create_test_file(db_session, name="second.png")
        first = create_test_file(db_session, name="first.png")
        attach_about_me_image_psql(str(about_me.id), str(second.id), sort_order=1, db_session=db_session)
        attach_about_me_image_psql(str(about_me.id), str(first.id), sort_order=0, db_session=db_session)

        result, _, ok = one_about_me_psql(db_session=db_session)

        assert ok is True
        assert [image.file_id for image in result.images] == [str(first.id), str(second.id)]
