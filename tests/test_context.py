import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_context_builder_init():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    assert builder.model is not None


def test_context_builder_custom_model():
    from evokb.context import ContextBuilder

    builder = ContextBuilder(model="gpt-4")
    assert builder.model == "gpt-4"


def test_build_context_returns_dict():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    snippets = [{"content": "Test fact", "path": "test.md"}]

    result = builder.build_context("test query", snippets, include_summary=False)

    assert "facts" in result
    assert "summary" in result
    assert "conflicts" in result
    assert result["query"] == "test query"
    assert result["source_count"] == 1


def test_build_context_without_dedupe():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    snippets = [
        {"content": "Fact 1", "path": "a.md"},
        {"content": "Fact 2", "path": "b.md"},
    ]

    result = builder.build_context(
        "query", snippets, dedupe=False, include_summary=False
    )

    assert len(result["facts"]) == 2


def test_build_context_excludes_conflicts():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    snippets = [{"content": "Fact", "path": "a.md"}]

    result = builder.build_context("query", snippets, include_conflicts=False)

    assert result["conflicts"] == []


@patch("evokb.context.completion")
def test_summarize_returns_string(mock_completion):
    from evokb.context import ContextBuilder

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="This is a summary."))]
    mock_completion.return_value = mock_response

    builder = ContextBuilder()
    snippets = [{"content": "Some test content", "path": "test.md"}]

    result = builder.summarize(snippets)

    assert isinstance(result, str)


@patch("evokb.context.completion")
def test_detect_conflicts_returns_list(mock_completion):
    from evokb.context import ContextBuilder

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="[]"))]
    mock_completion.return_value = mock_response

    builder = ContextBuilder()
    snippets = [{"content": "Fact", "path": "a.md"}]

    result = builder.detect_conflicts(snippets)

    assert isinstance(result, list)


def test_build_context_convenience_function():
    from evokb.context import build_context

    result = build_context("test query", [{"content": "fact", "path": "test.md"}])

    assert "facts" in result
    assert "query" in result


def test_context_builder_handles_empty_snippets():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()

    result = builder.build_context("query", [])

    assert result["facts"] == []
    assert result["source_count"] == 0
