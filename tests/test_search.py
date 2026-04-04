import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from evokb.search import SearchIndex


def test_search_index_init(tmp_path):
    index_dir = str(tmp_path / "test_index")
    search = SearchIndex(index_dir=index_dir)

    assert search.indexed_files == {}
    assert search.index_dir == index_dir


def test_search_index_documents(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()

    (wiki_dir / "test1.md").write_text("# Test 1\nSome content about AI")
    (wiki_dir / "test2.md").write_text("# Test 2\nMore content about ML")

    index_dir = str(tmp_path / "index")
    search = SearchIndex(index_dir=index_dir)
    search.index_documents(wiki_dir)

    assert len(search.indexed_files) == 2


def test_search_returns_list(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# AI\nArtificial Intelligence is great")

    search = SearchIndex()
    search.index_documents(wiki_dir)

    results = search.search("Artificial Intelligence", top_k=5)

    assert isinstance(results, list)
    assert len(results) > 0


def test_search_with_scoring(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Machine Learning\nML content here")

    search = SearchIndex()
    search.index_documents(wiki_dir)

    results = search.search("Machine Learning", top_k=1)

    assert results[0]["score"] > 0


def test_search_rebuild_index(tmp_path):
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Content")

    search = SearchIndex()
    search.rebuild_index(wiki_dir)

    assert len(search.indexed_files) == 1


def test_search_kb_convenience_function(tmp_path):
    from evokb.search import search_kb

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Python\nPython programming language")

    results = search_kb("Python", wiki_dir=wiki_dir)

    assert isinstance(results, list)
    assert len(results) > 0


def test_index_wiki_convenience_function(tmp_path):
    from evokb.search import index_wiki

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Content")

    index_wiki(wiki_dir)

    # Just verify it runs without error
    assert True


# Backward compatibility alias
TantivySearch = SearchIndex
