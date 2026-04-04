import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_tantivy_search_init(tmp_path):
    from evokb.search import TantivySearch

    index_dir = str(tmp_path / "test_index")
    search = TantivySearch(index_dir=index_dir)

    assert search.index is not None
    assert Path(index_dir).exists()


def test_tantivy_search_index_documents(tmp_path):
    from evokb.search import TantivySearch

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()

    (wiki_dir / "test1.md").write_text("# Test 1\nSome content about AI")
    (wiki_dir / "test2.md").write_text("# Test 2\nMore content about ML")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)
    search.index_documents(wiki_dir)

    assert Path(index_dir).exists()


def test_tantivy_search_returns_list(tmp_path):
    from evokb.search import TantivySearch

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# AI\nArtificial Intelligence is great")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)
    search.index_documents(wiki_dir)

    results = search.search("Artificial Intelligence", top_k=5)

    assert isinstance(results, list)


def test_tantivy_search_with_scoring(tmp_path):
    from evokb.search import TantivySearch

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Machine Learning\nML content here")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)
    search.index_documents(wiki_dir)

    results = search.search("Machine Learning", top_k=1)

    if results:
        assert "score" in results[0]
        assert results[0]["score"] > 0


def test_tantivy_rebuild_index(tmp_path):
    from evokb.search import TantivySearch

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Content")

    index_dir = str(tmp_path / "index")
    search = TantivySearch(index_dir=index_dir)

    search.rebuild_index(wiki_dir)
    assert Path(index_dir).exists()


def test_search_kb_convenience_function(tmp_path):
    from evokb.search import search_kb

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Python\nPython programming language")

    # This should handle non-existent index gracefully
    results = search_kb("Python", wiki_dir=wiki_dir)

    assert isinstance(results, list)


def test_index_wiki_convenience_function(tmp_path):
    from evokb.search import index_wiki

    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "test.md").write_text("# Content")

    index_wiki(wiki_dir)

    assert Path("clusters/index").exists()
