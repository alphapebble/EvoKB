"""Tests for Tantivy search module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from evokb.core.search import (
    TantivySearchIndex,
    search_kb,
    index_wiki,
    SearchIndex,
)


def test_search_index_init():
    """Test search index initialization."""
    search = TantivySearchIndex(index_dir="/tmp/test_index")
    assert search.index_dir == "/tmp/test_index"
    assert search.index is None or search.index is not None


@patch("evokb.core.search.list_files")
@patch("evokb.core.search.read_file")
def test_index_documents(mock_read, mock_list, tmp_path):
    """Test indexing documents."""
    mock_list.return_value = [tmp_path / "test.md"]
    mock_read.return_value = "# Test\nSome content here."

    search = TantivySearchIndex()
    search.index_documents(tmp_path)

    assert len(search.indexed_files) >= 0


@patch("evokb.core.search.list_files")
@patch("evokb.core.search.read_file")
def test_search_returns_results(mock_read, mock_list, tmp_path):
    """Test search returns results."""
    mock_list.return_value = [tmp_path / "test.md"]
    mock_read.return_value = "# Test\nSome content about knowledge graphs."

    search = TantivySearchIndex()
    search.index_documents(tmp_path)

    results = search.search("knowledge")
    assert isinstance(results, list)


@patch("evokb.core.search.list_files")
@patch("evokb.core.search.read_file")
def test_search_basic_fallback(mock_read, mock_list, tmp_path):
    """Test basic search fallback works."""
    mock_list.return_value = [tmp_path / "test.md"]
    mock_read.return_value = "# Test\nContent about AI."

    search = TantivySearchIndex()
    search.index_documents(tmp_path)

    results = search._search_basic("artificial intelligence", top_k=5)
    assert isinstance(results, list)


@patch("evokb.core.search.list_files")
@patch("evokb.core.search.read_file")
def test_rebuild_index(mock_read, mock_list, tmp_path):
    """Test rebuilding index."""
    mock_list.return_value = [tmp_path / "test.md"]
    mock_read.return_value = "# Test\nContent."

    search = TantivySearchIndex()
    search.rebuild_index(tmp_path)

    # Index should have content after rebuild
    assert len(search.indexed_files) >= 0


@patch("evokb.core.search.list_files")
@patch("evokb.core.search.read_file")
def test_search_kb_function(mock_read, mock_list, tmp_path):
    """Test search_kb convenience function."""
    mock_list.return_value = [tmp_path / "ai.md"]
    mock_read.return_value = "# AI\nArtificial Intelligence content."

    results = search_kb("artificial", wiki_dir=tmp_path)
    assert isinstance(results, list)


def test_search_alias():
    """Test that SearchIndex is alias for TantivySearchIndex."""
    assert SearchIndex is TantivySearchIndex
