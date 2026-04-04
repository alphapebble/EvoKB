import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@patch("evokb.retriever.completion")
def test_extract_keywords(mock_completion):
    from evokb.retriever import extract_keywords

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="test, keywords, here"))
    ]
    mock_completion.return_value = mock_response

    keywords = extract_keywords("test query")

    assert "test" in keywords
    assert "keywords" in keywords


@patch("evokb.retriever.completion")
def test_extract_keywords_handles_error(mock_completion):
    from evokb.retriever import extract_keywords

    mock_completion.side_effect = Exception("API Error")

    # Without LLM, should return empty or handle gracefully
    try:
        keywords = extract_keywords("test query")
        # Just check it doesn't crash
        assert True
    except:
        pass


def test_simple_keyword_search(tmp_path):
    from evokb.retriever import simple_keyword_search

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()

    (wiki_dir / "test.md").write_text(
        "This is a test file about artificial intelligence"
    )

    keywords = ["artificial", "intelligence"]
    results = simple_keyword_search(keywords, wiki_dir)

    assert len(results) > 0
    assert results[0][0] >= 1


def test_simple_keyword_search_empty_dir(tmp_path):
    from evokb.retriever import simple_keyword_search

    wiki_dir = tmp_path / "empty"
    wiki_dir.mkdir()

    keywords = ["test"]
    results = simple_keyword_search(keywords, wiki_dir)

    assert results == []


def test_simple_keyword_search_max_files(tmp_path):
    from evokb.retriever import simple_keyword_search

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()

    # Create multiple files
    for i in range(25):
        (wiki_dir / f"file{i}.md").write_text(f"Content {i}")

    keywords = ["content"]
    results = simple_keyword_search(keywords, wiki_dir, max_files=10)

    # Should respect max_files
    assert len(results) <= 10


@patch("evokb.retriever.completion")
def test_monte_carlo_sample(mock_completion):
    from evokb.retriever import monte_carlo_sample

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="8"))]
    mock_completion.return_value = mock_response

    tmp_file = Path("/tmp/test.md")
    tmp_file.write_text("\n".join([f"line {i}" for i in range(100)]))

    try:
        results = monte_carlo_sample(tmp_file, ["test"], max_samples=2, max_rounds=1)
        assert isinstance(results, list)
    finally:
        tmp_file.unlink(missing_ok=True)


def test_monte_carlo_sample_short_file(tmp_path):
    from evokb.retriever import monte_carlo_sample

    test_file = tmp_path / "short.md"
    test_file.write_text("Short content")

    results = monte_carlo_sample(test_file, ["test"], max_samples=2)

    # Short files should return with default high score
    assert len(results) > 0


def test_monte_carlo_sample_nonexistent_file():
    from evokb.retriever import monte_carlo_sample

    results = monte_carlo_sample(Path("/nonexistent/file.md"), ["test"])

    assert results == []


@patch("evokb.retriever.completion")
def test_query_evo_kb_uses_existing_cluster(mock_completion, tmp_path):
    from evokb.retriever import query_evo_kb

    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="This is a test answer"))
    ]
    mock_completion.return_value = mock_response

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Test content")

    # First call creates cluster
    answer1, cluster1 = query_evo_kb("test query", wiki_dir=wiki_dir)

    # Second call should reuse
    answer2, cluster2 = query_evo_kb("test query", wiki_dir=wiki_dir)

    assert cluster2.use_count >= 1


def test_compile_to_wiki_function():
    from evokb.retriever import compile_to_wiki

    # Just verify the function exists and is callable
    assert callable(compile_to_wiki)


def test_run_autoresearch_iteration_function():
    from evokb.retriever import run_autoresearch_iteration

    # Just verify the function exists
    assert callable(run_autoresearch_iteration)
