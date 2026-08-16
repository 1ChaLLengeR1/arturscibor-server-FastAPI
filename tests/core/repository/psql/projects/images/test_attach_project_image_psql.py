from core.repository.psql.projects.images.attach import attach_project_image_psql
from database.psql.models.projects import ProjectImage
from tests.core.repository.psql.file.helper import create_test_file
from tests.core.repository.psql.projects.helper import create_test_project


class TestAttachProjectImagePsql:
    def test_attach01_returns_ok(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)

        _, err, ok = attach_project_image_psql(str(project.id), str(file.id), sort_order=0, db_session=db_session)

        assert ok is True and err is None

    def test_attach02_row_persisted_with_sort_order(self, db_session):
        project = create_test_project(db_session)
        file = create_test_file(db_session)

        attach_project_image_psql(str(project.id), str(file.id), sort_order=3, db_session=db_session)

        image = db_session.query(ProjectImage).filter(ProjectImage.file_id == file.id).first()
        assert image is not None
        assert image.project_id == project.id
        assert image.sort_order == 3

    def test_attach03_same_file_twice_returns_conflict(self, db_session):
        project = create_test_project(db_session)
        other_project = create_test_project(db_session, name="Other")
        file = create_test_file(db_session)
        attach_project_image_psql(str(project.id), str(file.id), sort_order=0, db_session=db_session)

        _, err, ok = attach_project_image_psql(
            str(other_project.id), str(file.id), sort_order=0, db_session=db_session
        )

        assert ok is False
        assert err.key_type_error == "AlreadyAttached"
