from core.repository.psql.cv.one import one_cv_file_psql
from database.psql.models.file import FileType
from tests.core.repository.psql.cv.helper import create_test_cv
from tests.core.repository.psql.file.helper import create_test_file


class TestOneCvFilePsql:
    def test_one01_not_seeded_returns_not_found(self, db_session):
        result, err, ok = one_cv_file_psql(db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"

    def test_one02_seeded_without_file_returns_not_found(self, db_session):
        create_test_cv(db_session)

        result, err, ok = one_cv_file_psql(db_session=db_session)

        assert ok is False and result is None
        assert err.key_type_error == "NotFound"

    def test_one03_seeded_with_file_returns_file_data(self, db_session):
        file = create_test_file(
            db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf", directory="cv", mime_type="application/pdf"
        )
        create_test_cv(db_session, file_id=str(file.id))

        result, err, ok = one_cv_file_psql(db_session=db_session)

        assert ok is True and err is None
        assert result.file_id == str(file.id)
        assert result.directory == "cv"
        assert result.name == file.name
        assert result.original_name == "cv.pdf"
        assert result.mime_type == "application/pdf"
