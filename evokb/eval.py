"""Evaluation metrics for EvoKB."""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter


def evaluate_scraping_quality(
    scraped_path: Path, reference_path: Path = None
) -> Dict[str, float]:
    """
    Evaluate scraping quality metrics.

    Metrics:
    - Content density: ratio of meaningful text to total
    - Cleanliness: removed navigation/boilerplate?
    - Completeness: key sections captured?
    """
    if not scraped_path.exists():
        return {"error": "File not found"}

    content = scraped_path.read_text()

    # Basic metrics
    lines = content.split("\n")
    non_empty_lines = [l for l in lines if l.strip()]
    total_chars = len(content)

    # Estimate content density (remove short lines likely nav/footer)
    meaningful_lines = [l for l in non_empty_lines if len(l.strip()) > 20]
    content_density = len(meaningful_lines) / max(len(non_empty_lines), 1)

    # Check for common boilerplate
    boilerplate_patterns = [
        "cookie",
        "privacy",
        "terms of service",
        "all rights reserved",
        "subscribe",
        "newsletter",
        "follow us",
        "share on",
    ]
    boilerplate_count = sum(
        1 for p in boilerplate_patterns if p.lower() in content.lower()
    )
    cleanliness = 1.0 - (boilerplate_count / len(boilerplate_patterns))

    # Structure metrics
    has_title = any(l.startswith("#") for l in lines)
    has_headers = sum(1 for l in lines if l.startswith("##")) >= 2
    has_links = "[" in content and "](" in content

    return {
        "total_chars": total_chars,
        "total_lines": len(lines),
        "meaningful_lines": len(meaningful_lines),
        "content_density": round(content_density, 3),
        "cleanliness": round(cleanliness, 3),
        "has_title": has_title,
        "has_headers": has_headers,
        "has_links": has_links,
        "overall_score": round((content_density + cleanliness) / 2, 3),
    }


def evaluate_retrieval_accuracy(
    query: str, expected_docs: List[str], retrieved_docs: List[str]
) -> Dict[str, float]:
    """
    Evaluate retrieval quality metrics.

    Metrics:
    - Precision: fraction of retrieved that are relevant
    - Recall: fraction of relevant that were retrieved
    - F1: harmonic mean
    """
    expected_set = set(expected_docs)
    retrieved_set = set(retrieved_docs)

    true_positives = len(expected_set & retrieved_set)
    false_positives = len(retrieved_set - expected_set)
    false_negatives = len(expected_set - retrieved_set)

    precision = true_positives / max(len(retrieved_set), 1)
    recall = true_positives / max(len(expected_set), 1)
    f1 = 2 * precision * recall / max(precision + recall, 0.001)

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def evaluate_qa_accuracy(
    predicted_answer: str, expected_answer: str, context: str = None
) -> Dict[str, float]:
    """
    Evaluate Q&A quality metrics.

    Metrics:
    - Length ratio: predicted vs expected length
    - Keyword overlap: shared important words
    - containment: does predicted contain expected?
    """
    pred_words = set(predicted_answer.lower().split())
    exp_words = set(expected_answer.lower().split())

    # Keyword overlap
    overlap = len(pred_words & exp_words) / max(len(exp_words), 1)

    # Length ratio
    length_ratio = len(predicted_answer) / max(len(expected_answer), 1)
    length_score = 1.0 - abs(1.0 - length_ratio)

    # Containment (does answer contain key info?)
    common_words = pred_words & exp_words
    containment = len(common_words) / max(len(exp_words), 1)

    # Simple BLEU-like score
    trigrams_pred = set(zip(*[predicted_answer.lower().split()[i:] for i in range(3)]))
    trigrams_exp = set(zip(*[expected_answer.lower().split()[i:] for i in range(3)]))
    trigram_overlap = len(trigrams_pred & trigrams_exp) / max(len(trigrams_exp), 1)

    return {
        "keyword_overlap": round(overlap, 3),
        "length_score": round(length_score, 3),
        "containment": round(containment, 3),
        "trigram_overlap": round(trigram_overlap, 3),
        "overall_score": round((overlap + containment + trigram_overlap) / 3, 3),
    }


def evaluate_search_quality(
    query: str, results: List[Dict[str, Any]], relevant_docs: List[str] = None
) -> Dict[str, float]:
    """
    Evaluate search quality.

    Metrics:
    - Result count
    - Average score
    - Top result relevance (if we have ground truth)
    """
    if not results:
        return {"result_count": 0, "avg_score": 0, "has_results": False}

    scores = [r.get("score", 0) for r in results]

    metrics = {
        "result_count": len(results),
        "avg_score": round(sum(scores) / len(scores), 3),
        "max_score": max(scores),
        "has_results": True,
        "top_title": results[0].get("title", "unknown"),
    }

    # If we have ground truth, calculate MRR
    if relevant_docs:
        relevant_set = set(relevant_docs)
        for i, r in enumerate(results):
            if r.get("title") in relevant_set:
                metrics["mrr"] = 1.0 / (i + 1)  # Mean Reciprocal Rank
                break
        else:
            metrics["mrr"] = 0.0

    return metrics


def run_full_evaluation(
    wiki_dir: Path, test_queries: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Run full evaluation suite on the knowledge base.

    test_queries format:
    [
        {
            "query": "What is X?",
            "expected_docs": ["doc1", "doc2"],
            "expected_answer": "X is..."
        },
        ...
    ]
    """
    from .search import search_kb
    from .retriever import query_evo_kb

    results = {"search": [], "qa": [], "scraping": []}

    for test in test_queries:
        query = test["query"]

        # Evaluate search
        search_results = search_kb(query, wiki_dir)
        search_metrics = evaluate_search_quality(
            query, search_results, test.get("relevant_docs", [])
        )
        results["search"].append({"query": query, "metrics": search_metrics})

        # Evaluate Q&A if expected answer provided
        if "expected_answer" in test:
            try:
                answer, _ = query_evo_kb(query, wiki_dir)
                qa_metrics = evaluate_qa_accuracy(answer, test["expected_answer"])
                results["qa"].append({"query": query, "metrics": qa_metrics})
            except Exception as e:
                results["qa"].append({"query": query, "error": str(e)})

    # Calculate averages
    if results["search"]:
        valid_search = [
            s for s in results["search"] if "metrics" in s.get("metrics", {})
        ]
        if valid_search:
            avg_precision = sum(s["metrics"].get("mrr", 0) for s in valid_search) / len(
                valid_search
            )
            results["search_avg_mrr"] = round(avg_precision, 3)

    if results["qa"]:
        valid_qa = [q for q in results["qa"] if "metrics" in q]
        if valid_qa:
            avg_score = sum(q["metrics"]["overall_score"] for q in valid_qa) / len(
                valid_qa
            )
            results["qa_avg_score"] = round(avg_score, 3)

    return results


def save_evaluation_report(results: Dict[str, Any], output_path: Path):
    """Save evaluation results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Saved evaluation to {output_path}")
