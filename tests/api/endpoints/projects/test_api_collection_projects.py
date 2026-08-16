from api.endpoints.projects.collection import router as projects_collection_router
from api.endpoints.urls import PROJECTS_COLLECTION
from database.psql.models.projects import ProjectLevel
from tests.api.endpoints.projects.helper import make_client
from tests.core.repository.psql.projects.helper import create_test_project


class TestApiCollectionProjects:
    def test_collection01_returns_200_with_empty_list(self, db_session):
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_collection02_no_auth_required(self, db_session):
        create_test_project(db_session, name="Portfolio API")
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_collection03_ordered_by_numeric(self, db_session):
        create_test_project(db_session, name="Second", numeric=2)
        create_test_project(db_session, name="First", numeric=1)
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        names = [project["name"] for project in response.json()["data"]]
        assert names == ["First", "Second"]

    def test_collection04_includes_images_field(self, db_session):
        create_test_project(db_session, name="Portfolio API")
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        assert response.json()["data"][0]["images"] == []

    def test_collection05_defaults_to_polish(self, db_session):
        create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        assert response.json()["data"][0]["short_description"] == "Wąż"

    def test_collection06_lang_query_param_resolves_english(self, db_session):
        create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION, params={"lang": "en"})

        assert response.json()["data"][0]["short_description"] == "Snake"

    def test_collection07_unknown_lang_falls_back_to_polish(self, db_session):
        create_test_project(db_session, short_description={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION, params={"lang": "de"})

        assert response.json()["data"][0]["short_description"] == "Wąż"

    def test_collection08_includes_technologies_and_level(self, db_session):
        create_test_project(db_session, technologies=["Python", "FastAPI"], level=ProjectLevel.ADVANCED)
        client = make_client(db_session, projects_collection_router)

        response = client.get(PROJECTS_COLLECTION)

        data = response.json()["data"][0]
        assert data["technologies"] == ["Python", "FastAPI"]
        assert data["level"] == "advanced"
