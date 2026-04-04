import pytest
from pathlib import Path


def test_knowledge_cluster_creation():
    from evokb.memory.cluster import KnowledgeCluster

    cluster = KnowledgeCluster(
        query="test query",
        evidences=[{"file": "test.md", "snippet": "test", "score": 8}],
        summary="test summary",
        confidence=85,
    )

    assert cluster.query == "test query"
    assert cluster.confidence == 85
    assert cluster.use_count == 1
    assert len(cluster.history) == 1
    assert cluster.history[0] == "test query"


def test_cluster_to_dict():
    from evokb.memory.cluster import KnowledgeCluster

    cluster = KnowledgeCluster(
        query="test", evidences=[], summary="summary", confidence=80
    )

    data = cluster.to_dict()

    assert data["query"] == "test"
    assert data["confidence"] == 80
    assert "id" in data
    assert "created_at" in data
    assert "last_used" in data


def test_cluster_from_dict():
    from evokb.memory.cluster import KnowledgeCluster

    original = KnowledgeCluster(
        query="original query", evidences=[], summary="original summary", confidence=75
    )

    data = original.to_dict()
    restored = KnowledgeCluster.from_dict(data)

    assert restored.query == "original query"
    assert restored.confidence == 75
    assert restored.id == original.id


def test_cluster_use_count_increment():
    from evokb.memory.cluster import KnowledgeCluster

    cluster = KnowledgeCluster(
        query="test", evidences=[], summary="summary", confidence=80
    )

    initial_count = cluster.use_count
    cluster.use_count += 1

    assert cluster.use_count == initial_count + 1


def test_cluster_history_append():
    from evokb.memory.cluster import KnowledgeCluster

    cluster = KnowledgeCluster(
        query="query1", evidences=[], summary="summary", confidence=80
    )

    cluster.history.append("query2")

    assert len(cluster.history) == 2
    assert "query2" in cluster.history
