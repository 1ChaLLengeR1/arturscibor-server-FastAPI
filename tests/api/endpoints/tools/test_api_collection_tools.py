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
        create_test_tool(db_session, name="Python")
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_collection03_ordered_by_numeric(self, db_session):
        create_test_tool(db_session, name="Second", numeric=2)
        create_test_tool(db_session, name="First", numeric=1)
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        names = [tool["name"] for tool in response.json()["data"]]
        assert names == ["First", "Second"]

    def test_collection04_includes_images_field(self, db_session):
        create_test_tool(db_session, name="Python")
        client = make_client(db_session, tools_collection_router)

        response = client.get(TOOLS_COLLECTION)

        assert response.json()["data"][0]["images"] == []
