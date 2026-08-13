from api.endpoints.aboutme.get import router as aboutme_get_router
from api.endpoints.urls import ABOUT_ME
from tests.api.endpoints.aboutme.helper import make_client
from tests.core.repository.psql.aboutme.helper import create_test_about_me


class TestApiGetAboutMe:
    def test_get01_returns_404_when_not_seeded(self, db_session):
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME)

        assert response.status_code == 404

    def test_get02_returns_seeded_data(self, db_session):
        create_test_about_me(db_session, name="Artur Ścibor", job_title={"pl": "Programista", "en": "Developer"})
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Artur Ścibor"
        assert data["job_title"] == "Programista"

    def test_get03_no_auth_required(self, db_session):
        create_test_about_me(db_session)
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME)

        assert response.status_code == 200

    def test_get04_lang_query_param_resolves_english(self, db_session):
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME, params={"lang": "en"})

        assert response.json()["data"]["job_title"] == "Developer"

    def test_get05_unknown_lang_falls_back_to_polish(self, db_session):
        create_test_about_me(db_session, job_title={"pl": "Programista", "en": "Developer"})
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME, params={"lang": "de"})

        assert response.json()["data"]["job_title"] == "Programista"

    def test_get06_includes_images_field(self, db_session):
        create_test_about_me(db_session)
        client = make_client(db_session, aboutme_get_router)

        response = client.get(ABOUT_ME)

        assert response.json()["data"]["images"] == []
