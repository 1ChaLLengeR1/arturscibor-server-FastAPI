import uuid

from core.repository.psql.file.init import init_file_psql
from database.psql.models.file import File, FileStatus, FileType


class TestInitFilePsql:
    def test_init01_returns_ok(self, db_session):
        result, err, ok = init_file_psql(
            original_name="photo.png",
            name="abc_photo.png",
            size=2048,
            directory="projects",
            file_type=FileType.PHOTO,
            mime_type="image/png",
            db_session=db_session,
        )

        assert ok is True and err is None
        assert result.id

    def test_init02_status_is_pending(self, db_session):
        result, _, ok = init_file_psql(
            original_name="photo.png",
            name="abc_photo.png",
            size=2048,
            directory="projects",
            file_type=FileType.PHOTO,
            db_session=db_session,
        )

        assert ok is True
        assert result.status == FileStatus.PENDING.value

    def test_init03_fields_match_input(self, db_session):
        result, _, ok = init_file_psql(
            original_name="cat.jpg",
            name="uuid_cat.jpg",
            size=5000,
            directory="tools",
            file_type=FileType.PHOTO,
            mime_type="image/jpeg",
            db_session=db_session,
        )

        assert ok is True
        assert result.original_name == "cat.jpg"
        assert result.name == "uuid_cat.jpg"
        assert result.size == 5000
        assert result.directory == "tools"
        assert result.file_type == FileType.PHOTO.value
        assert result.mime_type == "image/jpeg"

    def test_init04_id_is_valid_uuid_and_row_persisted(self, db_session):
        result, _, ok = init_file_psql(
            original_name="photo.png",
            name="abc_photo.png",
            size=1024,
            directory="projects",
            file_type=FileType.PHOTO,
            db_session=db_session,
        )

        assert ok is True
        uuid.UUID(result.id)
        assert db_session.query(File).count() == 1
