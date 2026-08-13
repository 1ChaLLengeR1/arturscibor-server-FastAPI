from core.repository.psql.cv.update import set_cv_file_psql
from database.psql.models.file import FileType
from tests.core.repository.psql.cv.helper import create_test_cv
from tests.core.repository.psql.file.helper import create_test_file


class TestSetCvFilePsql:
    def test_set01_sets_file(self, db_session):
        create_test_cv(db_session)
        file = create_test_file(db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf")

        result, err, ok = set_cv_file_psql(str(file.id), db_session=db_session)

        assert ok is True and err is None
        assert result.file_id == str(file.id)

    def test_set02_resolves_url(self, db_session):
        create_test_cv(db_session)
        file = create_test_file(db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf")
        file.url = "/static/cv/cv.pdf"
        db_session.flush()

        result, _, ok = set_cv_file_psql(str(file.id), db_session=db_session)

        assert ok is True
        assert result.url == "/static/cv/cv.pdf"

    def test_set03_none_clears_file(self, db_session):
        file = create_test_file(db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf")
        create_test_cv(db_session, file_id=str(file.id))

        result, _, ok = set_cv_file_psql(None, db_session=db_session)

        assert ok is True
        assert result.file_id is None
        assert result.url is None

    def test_set04_not_seeded_returns_not_found(self, db_session):
        file = create_test_file(db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf")

        _, err, ok = set_cv_file_psql(str(file.id), db_session=db_session)

        assert ok is False
        assert err.key_type_error == "NotFound"
