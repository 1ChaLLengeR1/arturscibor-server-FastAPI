import uuid

from core.repository.psql.projects.delete import delete_project_psql
from database.psql.models.projects import Projects
from tests.core.repository.psql.projects.helper import create_test_project


class TestDeleteProjectPsql:
    def test_delete01_returns_ok(self, db_session):
        project = create_test_project(db_session)

        _, err, ok = delete_project_psql(str(project.id), db_session=db_session)

        assert ok is True and err is None

    def test_delete02_row_removed_from_db(self, db_session):
        project = create_test_project(db_session)

        delete_project_psql(str(project.id), db_session=db_session)

        assert db_session.query(Projects).filter(Projects.id == project.id).first() is None

    def test_delete03_nonexistent_returns_not_found(self, db_session):
        _, err, ok = delete_project_psql(str(uuid.uuid4()), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
