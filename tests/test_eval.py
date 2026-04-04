"""Test cases for EvoKB evaluation - for Codex/CI testing."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_scraping_quality_metrics():
    """Test scraping quality evaluation."""
    from evokb.eval import evaluate_scraping_quality

    # Create test file
    test_content = """# Test Document

This is a test document with meaningful content.
It has several paragraphs of actual information.
Not just short navigation links.
"""
    test_file = Path("/tmp/test_doc.md")
    test_file.write_text(test_content)

    metrics = evaluate_scraping_quality(test_file)

    assert metrics["content_density"] > 0
    assert metrics["cleanliness"] > 0
    assert metrics["overall_score"] > 0

    test_file.unlink()


def test_retrieval_accuracy():
    """Test retrieval accuracy metrics."""
    from evokb.eval import evaluate_retrieval_accuracy

    metrics = evaluate_retrieval_accuracy(
        query="test", expected_docs=["doc1", "doc2"], retrieved_docs=["doc1", "doc3"]
    )

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert metrics["precision"] == 0.5


def test_qa_accuracy():
    """Test Q&A accuracy metrics."""
    from evokb.eval import evaluate_qa_accuracy

    metrics = evaluate_qa_accuracy(
        predicted_answer="A knowledge graph is a structured representation of information",
        expected_answer="A knowledge graph represents information as interconnected entities",
    )

    assert "keyword_overlap" in metrics
    assert "containment" in metrics
    assert "overall_score" in metrics
    assert 0 <= metrics["overall_score"] <= 1


def test_search_quality():
    """Test search quality metrics."""
    from evokb.eval import evaluate_search_quality

    results = [
        {"title": "doc1", "score": 5},
        {"title": "doc2", "score": 3},
    ]

    metrics = evaluate_search_quality("test query", results)

    assert metrics["result_count"] == 2
    assert metrics["has_results"] is True
    assert "avg_score" in metrics


def test_search_quality_no_results():
    """Test search with no results."""
    from evokb.eval import evaluate_search_quality

    metrics = evaluate_search_quality("test query", [])

    assert metrics["result_count"] == 0
    assert metrics["has_results"] is False


def test_qa_accuracy_with_ground_truth():
    """Test Q&A with ground truth evaluation."""
    from evokb.eval import evaluate_qa_accuracy

    # Perfect answer
    perfect = evaluate_qa_accuracy(
        predicted_answer="Machine learning is a subset of AI",
        expected_answer="Machine learning is a subset of AI",
    )
    assert perfect["overall_score"] > 0.8

    # Partial match
    partial = evaluate_qa_accuracy(
        predicted_answer="ML is a type of artificial intelligence",
        expected_answer="Machine learning is a subset of AI",
    )
    assert partial["overall_score"] > 0.1


def test_search_with_relevance():
    """Test search with relevant docs."""
    from evokb.eval import evaluate_search_quality

    results = [
        {"title": "kg_article", "score": 5},
        {"title": "other", "score": 1},
    ]

    metrics = evaluate_search_quality(
        "knowledge graph", results, relevant_docs=["kg_article"]
    )

    assert metrics.get("mrr", 0) == 1.0


def test_eval_module_imports():
    """Test that eval module imports correctly."""
    from evokb import eval

    assert hasattr(eval, "evaluate_scraping_quality")
    assert hasattr(eval, "evaluate_qa_accuracy")
    assert hasattr(eval, "evaluate_search_quality")
    assert hasattr(eval, "run_full_evaluation")


def test_reporting_module():
    """Test reporting functions."""
    from evokb.reporting import reporting

    assert hasattr(reporting, "run_and_report")
    assert hasattr(reporting, "generate_dashboard_html")
    assert hasattr(reporting, "print_metrics_table")


# Run tests with: pytest tests/test_eval.py -v
