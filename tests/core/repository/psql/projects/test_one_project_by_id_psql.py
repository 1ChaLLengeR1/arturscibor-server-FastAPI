import uuid

from core.repository.psql.projects.images.attach import attach_project_image_psql
from core.repository.psql.projects.one import one_project_by_id_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.projects.helper import create_test_project


class TestOneProjectByIdPsql:
    def test_one01_returns_project(self, db_session):
        project = create_test_project(db_session)

        result, err, ok = one_project_by_id_psql(str(project.id), db_session=db_session)

        assert ok is True and err is None
        assert result.id == str(project.id)

    def test_one02_no_images_returns_empty_list(self, db_session):
        project = create_test_project(db_session)

        result, _, ok = one_project_by_id_psql(str(project.id), db_session=db_session)

        assert ok is True
        assert result.images == []

    def test_one03_returns_attached_images_ordered_by_sort_order(self, db_session):
        project = create_test_project(db_session)
        second = create_test_file(db_session, name="second.png")
        first = create_test_file(db_session, name="first.png")
        attach_project_image_psql(str(project.id), str(second.id), sort_order=1, db_session=db_session)
        attach_project_image_psql(str(project.id), str(first.id), sort_order=0, db_session=db_session)

        result, _, ok = one_project_by_id_psql(str(project.id), db_session=db_session)

        assert ok is True
        assert [image.file_id for image in result.images] == [str(first.id), str(second.id)]

    def test_one04_nonexistent_returns_not_found(self, db_session):
        result, err, ok = one_project_by_id_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"

    def test_one05_resolves_requested_language(self, db_session):
        project = create_test_project(db_session, description={"pl": "Wąż", "en": "Snake"})

        result, _, ok = one_project_by_id_psql(str(project.id), lang="en", db_session=db_session)

        assert ok is True
        assert result.description == "Snake"

    def test_one06_falls_back_to_default_language_when_missing(self, db_session):
        # "de" nigdy nie było w JSONB (tylko pl/en) — fallback na DEFAULT_LANGUAGE_CODE.
        project = create_test_project(db_session, description={"pl": "Opis PL", "en": "Description EN"})

        result, _, ok = one_project_by_id_psql(str(project.id), lang="de", db_session=db_session)

        assert ok is True
        assert result.description == "Opis PL"
