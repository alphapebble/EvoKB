import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_search_index_creation(tmp_path):
    from evokb.search import TantivySearch

    # Create temp index
    index_dir = str(tmp_path / "test_index")
    search = TantivySearch(index_dir=index_dir)

    assert search.index is not None
    assert Path(index_dir).exists()


@patch("evokb.search.read_file")
def test_index_documents(mock_read_file, tmp_path):
    from evokb.search import TantivySearch

    # Create wiki dir with test files
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()

    (wiki_dir / "test1.md").write_text("# Test 1\nSome content about AI")
    (wiki_dir / "test2.md").write_text("# Test 2\nMore content about ML")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)
    search.index_documents(wiki_dir)

    # Index should be created
    assert Path(index_dir).exists()


def test_search_returns_results(tmp_path):
    from evokb.search import TantivySearch

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# AI\nArtificial Intelligence is great")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)
    search.index_documents(wiki_dir)

    results = search.search("Artificial Intelligence", top_k=5)

    assert isinstance(results, list)


def test_context_builder_init():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    assert builder.model is not None


@patch("evokb.context.completion")
def test_summarize(mock_completion):
    from evokb.context import ContextBuilder

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="This is a summary of the content."))
    ]
    mock_completion.return_value = mock_response

    builder = ContextBuilder()
    snippets = [{"content": "Some test content", "path": "test.md"}]

    result = builder.summarize(snippets)

    assert isinstance(result, str)


def test_build_context_returns_dict():
    from evokb.context import ContextBuilder

    builder = ContextBuilder()
    snippets = [{"content": "Test fact", "path": "test.md"}]

    # This will fail without LLM but should return structure
    result = builder.build_context("test query", snippets, include_summary=False)

    assert "facts" in result
    assert "summary" in result
    assert "conflicts" in result
    assert result["query"] == "test query"
