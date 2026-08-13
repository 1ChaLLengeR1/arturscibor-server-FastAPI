from api.endpoints.cv.get import router as cv_get_router
from api.endpoints.urls import CV
from database.psql.models.file import FileType
from tests.api.endpoints.cv.helper import make_client
from tests.core.repository.psql.cv.helper import create_test_cv
from tests.core.repository.psql.file.helper import create_test_file


class TestApiGetCv:
    def test_get01_returns_404_when_not_seeded(self, db_session):
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 404

    def test_get02_returns_200_with_null_url_when_no_file_uploaded(self, db_session):
        create_test_cv(db_session)
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["file_id"] is None
        assert data["url"] is None

    def test_get03_returns_file_url_when_uploaded(self, db_session):
        file = create_test_file(db_session, file_type=FileType.DOCUMENT, original_name="cv.pdf")
        file.url = "/static/cv/cv.pdf"
        db_session.flush()
        create_test_cv(db_session, file_id=str(file.id))
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["file_id"] == str(file.id)
        assert data["url"] == "/static/cv/cv.pdf"

    def test_get04_no_auth_required(self, db_session):
        create_test_cv(db_session)
        client = make_client(db_session, cv_get_router)

        response = client.get(CV)

        assert response.status_code == 200
