import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_api_root():
    from evokb.api import app

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


def test_api_health():
    from evokb.api import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("evokb.api.search_kb")
def test_api_search(mock_search):
    from evokb.api import app

    mock_search.return_value = [{"title": "Test", "path": "test.md", "score": 1.0}]

    client = TestClient(app)
    response = client.post("/search", json={"query": "test", "top_k": 5})

    assert response.status_code == 200
    assert "results" in response.json()


@patch("evokb.api.classify_query_details")
def test_api_classify(mock_classify):
    from evokb.api import app

    mock_classify.return_value = {"intent": "factual", "entities": ["AI"]}

    client = TestClient(app)
    response = client.post("/classify", json={"query": "What is AI?"})

    assert response.status_code == 200
    assert "intent" in response.json()


@patch("evokb.api.build_context")
def test_api_context(mock_build):
    from evokb.api import app

    mock_build.return_value = {"facts": [], "summary": ""}

    client = TestClient(app)
    response = client.post(
        "/context",
        json={
            "query": "test",
            "search_results": [{"content": "fact", "path": "test.md"}],
        },
    )

    assert response.status_code == 200


@patch("evokb.api.query_evo_kb")
def test_api_query_with_llm(mock_query):
    from evokb.api import app

    mock_cluster = MagicMock()
    mock_cluster.id = "test123"
    mock_cluster.confidence = 85
    mock_cluster.evidences = []
    mock_query.return_value = ("Answer text", mock_cluster)

    client = TestClient(app)
    response = client.post("/query", json={"query": "test question", "use_llm": True})

    assert response.status_code == 200
    assert "answer" in response.json()


@patch("evokb.api.search_kb")
def test_api_query_without_llm(mock_search):
    from evokb.api import app

    mock_search.return_value = [{"title": "Result"}]

    client = TestClient(app)
    response = client.post("/query", json={"query": "test", "use_llm": False})

    assert response.status_code == 200
    assert "results" in response.json()


@patch("evokb.api.index_wiki")
def test_api_index(mock_index):
    from evokb.api import app

    client = TestClient(app)
    response = client.post("/index", json={"wiki_path": None})

    assert response.status_code == 200


def test_api_index_not_found():
    from evokb.api import app

    client = TestClient(app)
    response = client.post("/index", json={"wiki_path": "/nonexistent"})

    # Should handle error gracefully (500 or 404 both acceptable)
    assert response.status_code in [404, 500]
