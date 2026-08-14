from api.endpoints.tools.collection import router as tools_collection_router
from api.endpoints.urls import TOOLS_COLLECTION
from tests.api.endpoints.tools.helper import make_client
from tests.core.repository.psql.tools.helper import create_test_tool


class TestApiCollectionTools:
    def test_collection01_returns_200_with_empty_list(self, db_session):
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_collection02_no_auth_required(self, db_session):
        create_test_tool(db_session, name={"pl": "Python", "en": "Python"})
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_collection03_ordered_by_numeric(self, db_session):
        create_test_tool(db_session, name={"pl": "Second", "en": "Second"}, numeric=2)
        create_test_tool(db_session, name={"pl": "First", "en": "First"}, numeric=1)
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        names = [tool["name"] for tool in response.json()["data"]]
        assert names == ["First", "Second"]

    def test_collection04_includes_images_field(self, db_session):
        create_test_tool(db_session, name={"pl": "Python", "en": "Python"})
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.json()["data"][0]["images"] == []

    def test_collection05_defaults_to_polish(self, db_session):
        create_test_tool(db_session, name={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.json()["data"][0]["name"] == "Wąż"

    def test_collection06_lang_query_param_resolves_english(self, db_session):
        create_test_tool(db_session, name={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION, params={"lang": "en"})

        assert response.json()["data"][0]["name"] == "Snake"

    def test_collection07_unknown_lang_falls_back_to_polish(self, db_session):
        create_test_tool(db_session, name={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION, params={"lang": "de"})

        assert response.json()["data"][0]["name"] == "Wąż"
