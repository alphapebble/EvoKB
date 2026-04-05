"""Tests for lint module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from evokb.eval.lint import (
    check_orphans,
    check_stale_claims,
    check_source_grounding,
    check_contradictions,
    run_lint,
    extract_links,
    extract_claims,
    extract_frontmatter,
)


def test_extract_frontmatter():
    content = """---
title: "Test Page"
source: "test.md"
tags: "ai, ml"
---

# Test content
This is a test page.
"""
    fm, body = extract_frontmatter(content)
    assert fm["title"] == "Test Page"
    assert fm["source"] == "test.md"
    assert "Test content" in body


def test_extract_frontmatter_no_fm():
    content = "# Test\nJust content"
    fm, body = extract_frontmatter(content)
    assert fm == {}
    assert "Test" in body


def test_extract_links():
    content = "This is [[knowledge graph]] and [[AI]]. See also [[ML]]."
    links = extract_links(content)
    assert "knowledge graph" in links
    assert "AI" in links
    assert "ML" in links


def test_extract_claims():
    content = """
# Header
This is a short line.
Knowledge graph is a structured representation of entities.
It refers to relationships between concepts.
"""
    claims = extract_claims(content)
    assert len(claims) >= 1


@patch("evokb.eval.lint.list_files")
@patch("evokb.eval.lint.read_file")
def test_check_orphans(mock_read, mock_list):
    mock_list.return_value = [
        Path("wiki/page1.md"),
        Path("wiki/page2.md"),
        Path("wiki/index.md"),
    ]
    mock_read.side_effect = [
        "# Page 1\nSee [[Page 2]].",
        "# Page 2\nSee [[Page 1]].",
        "# Index\nNo links.",
    ]

    result = check_orphans(Path("wiki"))
    assert result["total_pages"] == 3
    assert "index" in result["orphans"]


@patch("evokb.eval.lint.list_files")
@patch("evokb.eval.lint.read_file")
def test_check_source_grounding(mock_read, mock_list):
    mock_list.return_value = [
        Path("wiki/page1.md"),
    ]
    mock_read.side_effect = [
        "---\n---\nJust content without source.",
    ]

    result = check_source_grounding(Path("wiki"))
    assert result["count"] >= 0


@patch("evokb.eval.lint.list_files")
@patch("evokb.eval.lint.read_file")
def test_check_stale_claims_no_timestamp(mock_read, mock_list):
    mock_list.return_value = [Path("wiki/page1.md")]
    mock_read.side_effect = ["# Content\nNo frontmatter."]

    result = check_stale_claims(Path("wiki"))
    assert result["count"] == 1
    assert result["stale_claims"][0]["issue"] == "no_updated_timestamp"


@patch("evokb.eval.lint.list_files")
@patch("evokb.eval.lint.read_file")
def test_check_contradictions(mock_read, mock_list):
    mock_list.return_value = [Path("wiki/page1.md")]
    mock_read.return_value = "# Page\nEvery expert agrees. No disagreement exists."

    result = check_contradictions(Path("wiki"))
    assert "count" in result


@patch("evokb.eval.lint.list_files")
@patch("evokb.eval.lint.read_file")
def test_run_lint(mock_read, mock_list):
    mock_list.return_value = [Path("wiki/page1.md")]
    mock_read.return_value = "---\nsource: test.md\n---\n# Content\nJust content."

    result = run_lint(Path("wiki"))
    assert "health_score" in result
