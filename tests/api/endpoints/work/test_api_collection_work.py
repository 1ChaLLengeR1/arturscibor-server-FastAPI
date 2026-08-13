from api.endpoints.urls import WORK_COLLECTION
from api.endpoints.work.collection import router as work_collection_router
from tests.api.endpoints.work.helper import make_client
from tests.core.repository.psql.work.helper import create_test_work
from tests.core.repository.psql.work.items.helper import create_test_work_item


class TestApiCollectionWork:
    def test_collection01_returns_200_with_empty_list(self, db_session):
        client = make_client(db_session, work_collection_router)

        response = client.get(WORK_COLLECTION)

        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_collection02_no_auth_required(self, db_session):
        create_test_work(db_session, company_name="SPINETIME")
        client = make_client(db_session, work_collection_router)

        response = client.get(WORK_COLLECTION)

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_collection03_ordered_by_numeric(self, db_session):
        create_test_work(db_session, company_name="Second", numeric=2)
        create_test_work(db_session, company_name="First", numeric=1)
        client = make_client(db_session, work_collection_router)

        response = client.get(WORK_COLLECTION)

        names = [w["company_name"] for w in response.json()["data"]]
        assert names == ["First", "Second"]

    def test_collection04_includes_nested_items(self, db_session):
        work = create_test_work(db_session)
        create_test_work_item(db_session, work.id, title={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, work_collection_router)

        response = client.get(WORK_COLLECTION)

        items = response.json()["data"][0]["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Wąż"

    def test_collection05_lang_query_param_resolves_english(self, db_session):
        work = create_test_work(db_session)
        create_test_work_item(db_session, work.id, title={"pl": "Wąż", "en": "Snake"})
        client = make_client(db_session, work_collection_router)

        response = client.get(WORK_COLLECTION, params={"lang": "en"})

        assert response.json()["data"][0]["items"][0]["title"] == "Snake"
