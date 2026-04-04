#!/usr/bin/env python3
"""Test the router module."""

from evokb.core.router import detect_intent, route_query, Route, classify_intent


def test_detect_intent_sql():
    """Test SQL routing patterns."""
    assert detect_intent("What do I know about Sarah") == Route.SQL
    assert detect_intent("Who is John from Acme") == Route.SQL
    assert detect_intent("Meeting with Sarah") == Route.SQL
    assert detect_intent("Recent notes about project X") == Route.SQL
    assert detect_intent("Project status update") == Route.SQL


def test_detect_intent_wiki():
    """Test Wiki routing patterns."""
    assert detect_intent("What is a knowledge graph") == Route.WIKI
    assert detect_intent("Explain diffusion models") == Route.WIKI
    assert detect_intent("How does LLM inference work") == Route.WIKI
    assert detect_intent("Tell me about neural networks") == Route.WIKI


def test_detect_intent_search():
    """Test default search routing."""
    assert detect_intent("find information") == Route.SEARCH
    assert detect_intent("search for docs") == Route.SEARCH


def test_route_query():
    """Test full routing."""
    result = route_query("What is a knowledge graph")
    assert result["route"] == "wiki"
    assert result["confidence"] == "high"
    assert "explanation" in result["reason"].lower()


def test_classify_intent():
    """Test intent classification."""
    assert classify_intent("What is a knowledge graph") == "factual"
    assert classify_intent("Find the file") == "search"
    assert classify_intent("Who is John") == "lookup"


if __name__ == "__main__":
    test_detect_intent_sql()
    test_detect_intent_wiki()
    test_detect_intent_search()
    test_route_query()
    test_classify_intent()
    print("✓ All router tests passed")
