from core.repository.psql.file.collection import collection_files_psql
from database.psql.models.file import FileStatus, FileType
from tests.core.repository.psql.file.helper import create_test_file


class TestCollectionFilesPsql:
    def test_collection01_empty_returns_zero_total(self, db_session):
        result, err, ok = collection_files_psql(db_session=db_session)

        assert ok is True and err is None
        assert result.total == 0
        assert result.items == []

    def test_collection02_returns_all_files(self, db_session):
        create_test_file(db_session, directory="projects")
        create_test_file(db_session, directory="tools")

        result, _, ok = collection_files_psql(db_session=db_session)

        assert ok is True
        assert result.total == 2
        assert len(result.items) == 2

    def test_collection03_filters_by_directory(self, db_session):
        create_test_file(db_session, directory="projects")
        create_test_file(db_session, directory="tools")

        result, _, ok = collection_files_psql(directory="projects", db_session=db_session)

        assert ok is True
        assert result.total == 1
        assert result.items[0].directory == "projects"

    def test_collection04_filters_by_file_type(self, db_session):
        create_test_file(db_session, file_type=FileType.PHOTO, name="a.png")
        create_test_file(db_session, file_type=FileType.VIDEO, name="b.mp4", mime_type="video/mp4")

        result, _, ok = collection_files_psql(file_type=FileType.VIDEO, db_session=db_session)

        assert ok is True
        assert result.total == 1
        assert result.items[0].file_type == FileType.VIDEO.value

    def test_collection05_filters_by_status(self, db_session):
        create_test_file(db_session, status=FileStatus.PENDING, name="a.png")
        create_test_file(db_session, status=FileStatus.CONFIRMED, name="b.png")

        result, _, ok = collection_files_psql(status=FileStatus.CONFIRMED, db_session=db_session)

        assert ok is True
        assert result.total == 1
        assert result.items[0].status == FileStatus.CONFIRMED.value

    def test_collection06_filters_by_original_name(self, db_session):
        create_test_file(db_session, original_name="holiday-photo.png", name="a.png")
        create_test_file(db_session, original_name="cv.png", name="b.png")

        result, _, ok = collection_files_psql(original_name="holiday", db_session=db_session)

        assert ok is True
        assert result.total == 1
        assert result.items[0].original_name == "holiday-photo.png"

    def test_collection07_pagination_limit_and_offset(self, db_session):
        for i in range(3):
            create_test_file(db_session, name=f"file-{i}.png")

        page, _, ok = collection_files_psql(limit=2, offset=0, db_session=db_session)
        assert ok is True
        assert page.total == 3
        assert len(page.items) == 2

        next_page, _, ok = collection_files_psql(limit=2, offset=2, db_session=db_session)
        assert ok is True
        assert len(next_page.items) == 1
