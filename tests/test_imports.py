import pytest


def test_config_import():
    """Test that config module can be imported."""
    import evokb.config

    assert evokb.config.MODEL is not None


def test_utils_import():
    """Test that utils module can be imported."""
    import evokb.utils

    assert hasattr(evokb.utils, "read_file")


def test_cluster_import():
    """Test that cluster module can be imported."""
    import evokb.cluster

    assert hasattr(evokb.cluster, "KnowledgeCluster")


def test_evaluator_import():
    """Test that evaluator module can be imported."""
    import evokb.evaluator

    assert hasattr(evokb.evaluator, "score_change")


def test_search_import():
    """Test that search module can be imported."""
    import evokb.search

    assert hasattr(evokb.search, "TantivySearch")


def test_context_import():
    """Test that context module can be imported."""
    import evokb.context

    assert hasattr(evokb.context, "ContextBuilder")


def test_agent_import():
    """Test that agent module can be imported."""
    import evokb.agent

    assert hasattr(evokb.agent, "AgentClassifier")


def test_librarian_import():
    """Test that librarian module can be imported."""
    import evokb.librarian

    assert hasattr(evokb.librarian, "main")


def test_api_import():
    """Test that api module can be imported."""
    import evokb.api

    assert hasattr(evokb.api, "app")
