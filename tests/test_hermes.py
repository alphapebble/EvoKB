"""Tests for Hermes review gate."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from evokb.agents.hermes import Hermes, run_hermes


def test_hermes_init(tmp_path):
    """Test Hermes initialization."""
    hermes = Hermes(drafts_dir=tmp_path / "drafts", live_dir=tmp_path / "live")
    assert hermes.drafts_dir == tmp_path / "drafts"
    assert hermes.live_dir == tmp_path / "live"


def test_score_article():
    """Test article scoring."""
    hermes = Hermes()

    content = """# Test Article

This is a test article about knowledge graphs.
Knowledge graphs represent information as interconnected entities.

## Key Points
1. First point about graphs
2. Second point about entities

Sources: https://example.com
"""
    scores = hermes.score_article(content)

    assert "length" in scores
    assert "structure" in scores
    assert "total" in scores


def test_review_article():
    """Test article review."""
    hermes = Hermes()

    content = """# Test Article

This is a test article about knowledge graphs.
Knowledge graphs represent information as interconnected entities.

## Key Points
1. First point about graphs
2. Second point about entities
3. Third point about relationships

Sources: https://example.com
"""
    result = hermes.review_article("test.md", content)

    assert "scores" in result
    assert "decision" in result
    assert result["decision"] in ["promote", "needs_review", "reject"]


def test_review_article_short():
    """Test short article gets reviewed."""
    hermes = Hermes()

    content = "# Short\nJust a sentence."
    result = hermes.review_article("short.md", content)

    assert result["decision"] in ["reject", "needs_review"]


def test_review_all_drafts_empty(tmp_path):
    """Test review with no drafts."""
    hermes = Hermes(drafts_dir=tmp_path / "drafts")
    results = hermes.review_all_drafts()
    assert results == []


def test_get_stats():
    """Test getting Hermes statistics."""
    hermes = Hermes()

    stats = hermes.get_stats()
    assert "total_reviewed" in stats
    assert "promoted" in stats
    assert "needs_review" in stats
    assert "rejected" in stats


def test_get_article_score():
    """Test getting article score."""
    hermes = Hermes()

    score = hermes.get_article_score("nonexistent.md")
    assert score is None


def test_run_hermes():
    """Test run_hermes function."""
    hermes = Hermes()
    hermes.scores = {"articles": {}, "history": []}

    run_hermes()
