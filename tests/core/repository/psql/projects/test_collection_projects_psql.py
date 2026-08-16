from core.repository.psql.projects.collection import collection_projects_psql
from core.repository.psql.projects.images.attach import attach_project_image_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.projects.helper import create_test_project


class TestCollectionProjectsPsql:
    def test_collection01_empty_returns_empty_list(self, db_session):
        result, err, ok = collection_projects_psql(db_session=db_session)

        assert ok is True and err is None
        assert result == []

    def test_collection02_returns_all_projects(self, db_session):
        create_test_project(db_session, name="First", numeric=1)
        create_test_project(db_session, name="Second", numeric=2)

        result, _, ok = collection_projects_psql(db_session=db_session)

        assert ok is True
        assert len(result) == 2

    def test_collection03_ordered_by_numeric_ascending(self, db_session):
        create_test_project(db_session, name="Second", numeric=2)
        create_test_project(db_session, name="First", numeric=1)

        result, _, ok = collection_projects_psql(db_session=db_session)

        assert ok is True
        assert [project.name for project in result] == ["First", "Second"]

    def test_collection04_null_numeric_sorted_last(self, db_session):
        create_test_project(db_session, name="NoOrder", numeric=None)
        create_test_project(db_session, name="First", numeric=1)

        result, _, ok = collection_projects_psql(db_session=db_session)

        assert ok is True
        assert [project.name for project in result] == ["First", "NoOrder"]

    def test_collection05_includes_images_per_project(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)
        attach_project_image_psql(str(project.id), str(file.id), sort_order=0, db_session=db_session)

        result, _, ok = collection_projects_psql(db_session=db_session)

        assert ok is True
        assert len(result[0].images) == 1
        assert result[0].images[0].file_id == str(file.id)

    def test_collection06_resolves_requested_language_per_project(self, db_session):
        create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"}, numeric=1)

        result, _, ok = collection_projects_psql(lang="en", db_session=db_session)

        assert ok is True
        assert result[0].short_description == "Snake"
