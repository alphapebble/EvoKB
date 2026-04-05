"""Tests for indexer module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from evokb.eval.indexer import (
    generate_index,
    generate_log,
    update_index_and_log,
    extract_frontmatter,
    extract_summary,
)


def test_extract_frontmatter():
    content = """---
title: "Test Page"
source: "test.md"
tags: "ai, ml"
---

# Test content
This is a test page with meaningful content.
"""
    fm = extract_frontmatter(content)
    assert fm["title"] == "Test Page"
    assert fm["source"] == "test.md"
    assert fm["tags"] == "ai, ml"


def test_extract_summary():
    content = """---
title: Test
---

# Header
First line summary here.
Second line.
"""
    summary = extract_summary(content)
    assert "First line" in summary


def test_extract_summary_no_header():
    content = "Just some content without headers."
    summary = extract_summary(content)
    assert summary != ""


@patch("evokb.eval.indexer.list_files")
@patch("evokb.eval.indexer.read_file")
def test_generate_index(mock_read, mock_list):
    mock_list.return_value = [
        Path("/tmp/wiki/ai.md"),
    ]
    mock_read.side_effect = [
        """---
title: "Artificial Intelligence"
tags: "ai, tech"
summary: "AI overview"
---

# AI Content
""",
    ]

    index = generate_index(Path("/tmp/wiki"))
    assert "Wiki Index" in index


@patch("evokb.eval.indexer.list_files")
@patch("evokb.eval.indexer.read_file")
def test_generate_log(mock_read, mock_list):
    mock_list.return_value = [
        Path("/tmp/wiki/page1.md"),
    ]
    mock_read.side_effect = [
        """---
title: "Page 1"
created: "2026-04-01"
source: "test.md"
---

# Content
""",
    ]

    log = generate_log(Path("/tmp/wiki"))
    assert "Wiki Log" in log
    assert "Page 1" in log


def test_update_index_and_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        wiki = Path(tmpdir) / "wiki"
        wiki.mkdir()

        (wiki / "test.md").write_text("""---
title: "Test"
---

# Content
""")

        with patch("evokb.eval.indexer.WIKI_DIR", wiki):
            update_index_and_log(wiki)

        assert (wiki / "index.md").exists()
        assert (wiki / "log.md").exists()
