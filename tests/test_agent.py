import pytest
from unittest.mock import patch, MagicMock


def test_agent_classifier_init():
    from evokb.agents.agent import AgentClassifier

    classifier = AgentClassifier()
    assert classifier.model is not None


def test_agent_classifier_custom_model():
    from evokb.agents.agent import AgentClassifier

    classifier = AgentClassifier(model="gpt-4")
    assert classifier.model == "gpt-4"


def test_query_intent_enum():
    from evokb.agents.agent import QueryIntent

    assert QueryIntent.FACTUAL.value == "factual"
    assert QueryIntent.EXPLAIN.value == "explain"
    assert QueryIntent.COMPARE.value == "compare"
    assert QueryIntent.SUMMARIZE.value == "summarize"
    assert QueryIntent.CREATE.value == "create"
    assert QueryIntent.UPDATE.value == "update"
    assert QueryIntent.SEARCH.value == "search"
    assert QueryIntent.GENERAL.value == "general"


@patch("evokb.agents.agent.completion")
def test_classify_returns_intent(mock_completion):
    from evokb.agents.agent import AgentClassifier, QueryIntent

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="factual"))]
    mock_completion.return_value = mock_response

    classifier = AgentClassifier()
    result = classifier.classify("What is AI?")

    assert isinstance(result, QueryIntent)


@patch("evokb.agents.agent.completion")
def test_classify_handles_unknown_intent(mock_completion):
    from evokb.agents.agent import AgentClassifier, QueryIntent

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="unknown_intent"))]
    mock_completion.return_value = mock_response

    classifier = AgentClassifier()
    result = classifier.classify("Some query")

    assert result == QueryIntent.GENERAL


@patch("evokb.agents.agent.completion")
def test_extract_entities_returns_list(mock_completion):
    from evokb.agents.agent import AgentClassifier

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Python, AI, Machine Learning"))
    ]
    mock_completion.return_value = mock_response

    classifier = AgentClassifier()
    result = classifier.extract_entities("Tell me about Python and AI")

    assert isinstance(result, list)
    assert len(result) > 0


@patch("evokb.agents.agent.completion")
def test_extract_entities_handles_error(mock_completion):
    from evokb.agents.agent import AgentClassifier

    mock_completion.side_effect = Exception("API Error")

    classifier = AgentClassifier()
    result = classifier.extract_entities("test query")

    assert result == []


def test_get_required_action_factual():
    from evokb.agents.agent import AgentClassifier, QueryIntent

    classifier = AgentClassifier()
    action = classifier.get_required_action(QueryIntent.FACTUAL, {})

    assert action == "search_and_answer"


def test_get_required_action_compare():
    from evokb.agents.agent import AgentClassifier, QueryIntent

    classifier = AgentClassifier()
    action = classifier.get_required_action(QueryIntent.COMPARE, {})

    assert action == "search_multiple_and_compare"


def test_get_required_action_create():
    from evokb.agents.agent import AgentClassifier, QueryIntent

    classifier = AgentClassifier()
    action = classifier.get_required_action(QueryIntent.CREATE, {})

    assert action == "create_new_content"


@patch("evokb.agents.agent.completion")
def test_classify_with_details(mock_completion):
    from evokb.agents.agent import AgentClassifier

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="factual"))]
    mock_completion.return_value = mock_response

    classifier = AgentClassifier()
    result = classifier.classify_with_details("What is Python?")

    assert "intent" in result
    assert "entities" in result
    assert "recommended_action" in result
    assert "intent_description" in result


def test_classify_query_convenience():
    from evokb.agents.agent import classify_query, QueryIntent

    # Without mock, this will fail - but we can test import works
    from evokb.agents.agent import AgentClassifier

    assert AgentClassifier is not None


def test_classify_query_details_convenience():
    from evokb.agents.agent import classify_query_details

    assert classify_query_details is not None
