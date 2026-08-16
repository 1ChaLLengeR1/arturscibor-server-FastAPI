import uuid

from core.repository.psql.projects.images.attach import attach_project_image_psql
from core.repository.psql.projects.images.one import one_project_image_psql
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.projects.helper import create_test_project


class TestOneProjectImagePsql:
    def test_one01_returns_ok_when_attached(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)
        attach_project_image_psql(str(project.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = one_project_image_psql(str(project.id), str(file.id), db_session=db_session)

        assert ok is True and err is None

    def test_one02_not_attached_returns_not_found(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)

        _, err, ok = one_project_image_psql(str(project.id), str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_one03_attached_to_different_project_returns_not_found(self, db_session):
        project = create_test_project(db_session)
        other_project = create_test_project(db_session, name="Other")
        file = create_test_file(db_session)
        attach_project_image_psql(str(other_project.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = one_project_image_psql(str(project.id), str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"

    def test_one04_nonexistent_file_returns_not_found(self, db_session):
        project = create_test_project(db_session)

        _, err, ok = one_project_image_psql(str(project.id), str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
