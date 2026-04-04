import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_cluster_creation():
    from evokb.cluster import KnowledgeCluster

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


def test_cluster_to_dict():
    from evokb.cluster import KnowledgeCluster

    cluster = KnowledgeCluster(
        query="test", evidences=[], summary="summary", confidence=80
    )

    data = cluster.to_dict()

    assert data["query"] == "test"
    assert data["confidence"] == 80
    assert "id" in data
    assert "created_at" in data


def test_utils_read_file(tmp_path):
    from evokb.utils import read_file

    test_file = tmp_path / "test.md"
    test_file.write_text("# Test Content")

    content = read_file(test_file)
    assert content == "# Test Content"


def test_utils_read_nonexistent():
    from evokb.utils import read_file

    result = read_file(Path("/nonexistent/file.md"))
    assert result == ""


def test_utils_list_files(tmp_path):
    from evokb.utils import list_files

    (tmp_path / "file1.md").write_text("content")
    (tmp_path / "file2.md").write_text("content")

    files = list_files(tmp_path, "*.md")
    assert len(files) == 2


def test_utils_ensure_dir(tmp_path):
    from evokb.utils import ensure_dir

    new_dir = tmp_path / "new_folder"
    result = ensure_dir(new_dir)

    assert new_dir.exists()
    assert result == new_dir


def test_config_defaults():
    from evokb.config import MODEL, CHECK_INTERVAL

    assert MODEL == "ollama/llama3.2"
    assert CHECK_INTERVAL == 8


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
def test_simple_keyword_search(mock_completion, tmp_path):
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


def test_apply_change_creates_backup(tmp_path):
    from evokb.evaluator import apply_change

    test_file = tmp_path / "test.md"
    test_file.write_text("original content")

    result = apply_change(test_file, "new content")
    backup_file = tmp_path / "test.md.bak"

    assert result is True
    assert test_file.read_text() == "new content"
    assert backup_file.exists()
    assert backup_file.read_text() == "original content"


def test_revert_change(tmp_path):
    from evokb.evaluator import apply_change, revert_change

    test_file = tmp_path / "test.md"
    test_file.write_text("original")
    backup_file = tmp_path / "test.md.bak"
    backup_file.write_text("backup content")

    result = revert_change(test_file)

    assert result is True
    assert test_file.read_text() == "backup content"
    assert not backup_file.exists()


@patch("evokb.evaluator.completion")
def test_score_change(mock_completion):
    from evokb.evaluator import score_change

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content='{"clarity": 8, "grounding": 9, "overall": 8}')
        )
    ]
    mock_completion.return_value = mock_response

    result = score_change("test content", ["clarity", "grounding"])

    assert "overall" in result or "error" in result
