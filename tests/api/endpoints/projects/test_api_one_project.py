import uuid

from api.endpoints.projects.one import router as projects_one_router
from api.endpoints.urls import PROJECTS_ONE
from tests.api.endpoints.projects.helper import make_client
from tests.core.repository.psql.projects.helper import create_test_project


class TestApiOneProject:
    def test_one01_returns_200_with_full_data(self, db_session):
        project = create_test_project(db_session, name="Portfolio API")
        client = make_client(db_session, projects_one_router)

        response = client.get(PROJECTS_ONE.format(project_id=project.id))

        assert response.status_code == 200
        assert response.json()["data"]["id"] == str(project.id)
        assert response.json()["data"]["name"] == "Portfolio API"

    def test_one02_no_auth_required(self, db_session):
        project = create_test_project(db_session)
        client = make_client(db_session, projects_one_router)

        response = client.get(PROJECTS_ONE.format(project_id=project.id))

        assert response.status_code == 200

    def test_one03_nonexistent_returns_404(self, db_session):
        client = make_client(db_session, projects_one_router)

        response = client.get(PROJECTS_ONE.format(project_id=uuid.uuid4()))

        assert response.status_code == 404

    def test_one04_lang_query_param_resolves_english(self, db_session):
        project = create_test_project(db_session, description={"pl": "Opis PL", "en": "Description EN"})
        client = make_client(db_session, projects_one_router)

        response = client.get(PROJECTS_ONE.format(project_id=project.id), params={"lang": "en"})

        assert response.json()["data"]["description"] == "Description EN"

    def test_one05_unknown_lang_falls_back_to_polish(self, db_session):
        project = create_test_project(db_session, description={"pl": "Opis PL", "en": "Description EN"})
        client = make_client(db_session, projects_one_router)

        response = client.get(PROJECTS_ONE.format(project_id=project.id), params={"lang": "de"})

        assert response.json()["data"]["description"] == "Opis PL"
