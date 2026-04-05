"""Tests for provenance module."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from evokb.eval import provenance


@patch("evokb.eval.provenance.WIKI_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
def test_track_source(mock_wiki_dir):
    mock_wiki_dir.mkdir(exist_ok=True, parents=True)

    record = provenance.track_source(
        file_name="test.md",
        source="raw/test.md",
        source_type="file",
    )

    assert record["file"] == "test.md"
    assert record["source"] == "raw/test.md"
    assert record["source_type"] == "file"
    assert "tracked_at" in record


@patch("evokb.eval.provenance.WIKI_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
def test_get_provenance(mock_wiki_dir):
    mock_wiki_dir.mkdir(exist_ok=True, parents=True)

    provenance.track_source(
        file_name="test.md",
        source="raw/test.md",
        source_type="file",
    )

    record = provenance.get_provenance("test.md")
    assert record is not None
    assert record["file"] == "test.md"


@patch("evokb.eval.provenance.WIKI_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
def test_get_all_provenance(mock_wiki_dir):
    mock_wiki_dir.mkdir(exist_ok=True, parents=True)
    provenance.PROVENANCE_FILE.unlink(missing_ok=True)

    provenance.track_source("file1.md", "raw/1.md", "file")
    provenance.track_source("file2.md", "raw/2.md", "file")

    records = provenance.get_all_provenance()
    assert len(records) >= 2


@patch("evokb.eval.provenance.WIKI_DIR", new_callable=lambda: Path(tempfile.mkdtemp()))
def test_link_query_to_file(mock_wiki_dir):
    mock_wiki_dir.mkdir(exist_ok=True, parents=True)

    provenance.track_source("test.md", "raw/test.md", "file")
    provenance.link_query_to_file("test.md", "What is AI?")

    record = provenance.get_provenance("test.md")
    assert record["query"] == "What is AI?"
    assert "derived_from_query_at" in record
