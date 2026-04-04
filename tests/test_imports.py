"""Test that all modules can be imported."""

import pytest


def test_import_config():
    from evokb import config

    assert config.MODEL is not None


def test_import_utils():
    from evokb import utils

    assert hasattr(utils, "read_file")
    assert hasattr(utils, "list_files")


def test_import_cluster():
    from evokb import cluster

    assert hasattr(cluster, "KnowledgeCluster")


def test_import_retriever():
    from evokb import retriever

    assert hasattr(retriever, "query_evo_kb")


def test_import_evaluator():
    from evokb import evaluator

    assert hasattr(evaluator, "score_change")
    assert hasattr(evaluator, "apply_change")


def test_import_search():
    from evokb import search

    assert hasattr(search, "TantivySearch")
    assert hasattr(search, "search_kb")


def test_import_context():
    from evokb import context

    assert hasattr(context, "ContextBuilder")


def test_import_agent():
    from evokb import agent

    assert hasattr(agent, "AgentClassifier")
    assert hasattr(agent, "QueryIntent")


def test_import_api():
    from evokb import api

    assert hasattr(api, "app")


def test_import_librarian():
    from evokb import librarian

    assert hasattr(librarian, "main")


def test_package_exports():
    from evokb import query_evo_kb, KnowledgeCluster
    from evokb import TantivySearch, search_kb, index_wiki
    from evokb import ContextBuilder, build_context
    from evokb import AgentClassifier, classify_query, QueryIntent

    assert callable(query_evo_kb)
    assert callable(search_kb)
    assert callable(index_wiki)
    assert callable(build_context)
    assert callable(classify_query)
